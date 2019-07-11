#! /usr/bin/env python3

import argparse
from conllu import parse
import objet_baseline
import os
import time

parser = argparse.ArgumentParser(description="A partir des parametres donnes ainsi que des textes train (et dev), genere un lexique contenant les meilleurs parametres pour pouvoir identifier les expressions dans un texte inconnue")
parser.add_argument("--train", help="texte dans lequel on va relever les expressions", required=True)
parser.add_argument("--dev", help="texte, non obligatoire, permettant de trouver les paramtres optimaux pour identifier les expressions", required=False)
parser.add_argument("--all", help="", required=False)
parser.add_argument("--form", help="", required=False)
parser.add_argument("--lemma", help="", required=False)
parser.add_argument("--upostag", help="", required=False)
parser.add_argument("--deprel", help="", required=False)
parser.add_argument("--order", help="", required=False)
# parser.add_argument("--", help="", required=False) 
# parser.parse_args().train
# parser.parse_args().dev

if parser.parse_args().all == "true" :
	list_argument_form = [True, False]
	list_argument_lemma = [True, False]
	list_argument_upostag =[True, False]
	list_argument_deprel = [True, False]
	list_argument_order = [True, False]
else :
	list_argument_form = [True, False] if parser.parse_args().form == 'true' else [False]
	list_argument_lemma = [True, False] if parser.parse_args().lemma == 'true' else [False]
	list_argument_upostag = [True, False] if parser.parse_args().upostag == 'true' else [False]
	list_argument_deprel = [True, False] if parser.parse_args().deprel == 'true' else [False]
	list_argument_order = [True, False] if parser.parse_args().order == 'true' else [False]
	if not (list_argument_form[0] or list_argument_lemma[0]) :
		print("Erreur: il faut donner au moins mettre form ou lemma", file=os.sys.stderr)
		os.sys.exit()

os.system("mkdir baseline/temp_resultat")
os.system("rm baseline/temp_resultat/*")

### on va relever les expressions dans le texte train

# on fait une correction du texte dans le cas ou il contienne de petites erreurs (au vu de celles presentes dans les corpus), pour qu il puisse etre utilise par la methode parse du module conllu
def correction_texte_parse(texte) :
	temp = ""
	with open(str(texte), 'r') as mon_fichier:
		for ligne in mon_fichier :
			if ligne[0] == '#' :
				if ligne != "# newdoc\n" and ligne != "# newpar\n" :
					temp += ligne
				elif ligne == "# newdoc\n" :
					temp += "# newdoc id = 0\n"
				elif ligne == "# newpar\n" :
					temp += "# newpar id = 0\n"
			elif ligne == '\n' :
				temp += ligne
			else :
				ligne = ligne.split('\t')
				temp0 = str(ligne[0]) + '\t' + str(ligne[1])
				for i in ligne[2:] :
					temp0 += '\t'
					if i == '-' :
						temp0 += '_'
					else :	
						temp0 += i
				if temp[-1] != '\n' :
					temp0 += '\n'
				temp += temp0
	return parse(temp)

def blind(texte) :
	for phrase in texte :
		for mot_phrase in phrase :
			mot_phrase['PARSEME:MWE'] = '_'


# on releve les expressions a partir du texte precedement corrige
list_expression = []
for paragraphe_TokenList in correction_texte_parse(parser.parse_args().train) :
	list_temp = [[""]]
	for mot_OrderedDict in paragraphe_TokenList :
		if (mot_OrderedDict.get('PARSEME:MWE') != '*') :
			mwe_split = mot_OrderedDict.get('PARSEME:MWE').split(';')
			for numero_expression in mwe_split :
				numero_expression_split = numero_expression.split(':')
				while len(list_temp) < int(numero_expression_split[0]) :
					list_temp.append([""])
				if len(numero_expression_split) == 2 :
					list_temp[int(numero_expression_split[0]) - 1][0] = numero_expression_split[1]
				list_temp[int(numero_expression_split[0]) - 1].append(mot_OrderedDict)
	for expression in list_temp :
		if expression == [''] :
			continue
		expression_complete = objet_baseline.ExpressionComplete()
		expression_complete.setTag(expression[0])
		
		for mot in expression[1:] :
			mot_expression = objet_baseline.ExpressionWord(mot)
			expression_complete.add(mot_expression)
		
		compteur = 0
		for mot in expression_complete.getListWord() :
			mot.set('id', str(mot.get('id')) + ':' + str(compteur))
			compteur += 1
			mot.set('head', str(mot.get('head')) + '*')

		for mot in expression_complete.getListWord() :
			ancien_id = mot.get('id').split(':')[0]
			nouvel_id = mot.get('id').split(':')[1]
			mot.set('id', nouvel_id)
			for mot0 in expression_complete.getListWord() :
				if (mot0.get('head')[-1] == '*') and (mot0.get('head')[:-1] == ancien_id) :
					mot0.set('head', nouvel_id)
		for mot in expression_complete.getListWord() :
			if (mot.get('head')[-1] == '*') or (mot.get('deprel') in ['root','ROOT','tri']) :
				mot.set('head', '_')
				mot.set('deprel', '_')

		# on met en place un leger anti doublon afin de reduire leur nombre
		boolean = True
		for i in list_expression :
			if i.equals(expression_complete) :
				boolean = False
		if boolean :
			list_expression.append(expression_complete)

with open("baseline/temp_resultat/lexique.txt", 'w') as mon_fichier :
	for expression in list_expression :
		mon_fichier.write(expression.toString() + '\n')


if parser.parse_args().dev is None :
	os.system('echo lemma_upostag_deprel') # les parametres de la baseline par defaut
	os.system('echo ')
	os.system('cat baseline/temp_resultat/lexique.txt')
	os.sys.exit()


### on releve le texte (qui a deja etait corriger et mis en blind) dans lequel on va devoir trouver les expressions
texte_entre_initial = correction_texte_parse(parser.parse_args().dev)

texte_entre = []
for paragraphe in texte_entre_initial : # on va fragment le texte en morceau (entre 50 et 150 mots) de facon a ce que les paragraphes que seront traite ne soient pas trop long
	if len(paragraphe) >= 100 :
		i = 0
		while len(paragraphe[100*i:]) >= 150 : # on veut eviter que le dernier fragment soit trop court
			texte_entre.append(paragraphe[100*i:100*(i+1)])
			i += 1
		texte_entre.append(paragraphe[100*i:])
	else :
		texte_entre.append(paragraphe)



### Methode :

### methode de verification
def methode_verification(mot_expression, mot_phrase, argument_form, argument_lemma, argument_upostag, argument_deprel) :
	if not isinstance(mot_phrase.get('id'), int) :
		return False
	boolean = True
	if argument_form :
		boolean = boolean and (mot_expression.get('form') == mot_phrase['form'])
	if argument_lemma :
		boolean = boolean and (mot_expression.get('lemma') == mot_phrase['lemma'])
	if argument_upostag :
		boolean = boolean and (mot_expression.get('upostag') == mot_phrase['upostag'])
	if argument_deprel :
		boolean = boolean and ((mot_expression.get('deprel') == '_') or (mot_phrase['deprel'] in ['root','ROOT','tri']) or (mot_expression.get('deprel') == mot_phrase['deprel']))
	return boolean


### on cree la liste (de liste) dont chaque mot present dans un element de cette liste peut potentiellement correspondre a un mot de l expression actuellement traite. C est la premiere etape du traitement
def creation_list_combinaison(expression, phrase) :
	resultat = []
	for mot_expression in expression.getListWord() :
		resultat.append([])
		for mot_phrase in phrase :
			if methode_verification(mot_expression, mot_phrase, argument_form, argument_lemma, argument_upostag, argument_deprel) :
				resultat[-1].append(mot_phrase)
	return resultat

### on fait une modification au niveau des parseme_mwe afin de remplacer les 'None' par des '*' pour que l evaluation ne pose pas de probleme
def remplace_non_expression(phrase) :
	for mot_phrase in phrase :
		if mot_phrase.get('PARSEME:MWE') == '_' :
			mot_phrase['PARSEME:MWE'] = '*'

### on verifie que la potentiel expression que l on veut valider ne comporte pas plus d une fois le meme mot
### on fait la 2eme etape du traitement de facon a savoir si l expression potentiel et vraiment 'identique' par rapport a celle voulu (au niveau des liens entre les mots de l expression) 
def methode_verification_supplementaire(expression, combinaison, argument_order, argument_deprel) :
	temp_order = 0
	for mot in combinaison :
		if combinaison.count(mot) != 1 :
			return False
		if (mot['id'] < temp_order) and argument_order :
			return False
		temp_order = mot['id']
	if argument_deprel :
		for mot_expression in expression.getListWord() :
			if mot_expression.get('head') != '_' :
				if combinaison[int(mot_expression.get('id'))].get('head') != combinaison[int(mot_expression.get('head'))].get('id') :
					return False
	return True



# permettant d avoir ce qui se passe de facon plus precise
identifiant_max = 0
for i in [list_argument_upostag, list_argument_deprel, list_argument_order] :
	if i == [False] :
		continue
	identifiant_max = identifiant_max*2 + (1 if i[0] else 0)
identifiant_max = identifiant_max + 1
if (list_argument_form[0] == True) and (list_argument_lemma[0] == True) :
	identifiant_max = identifiant_max * 3
identifiant_max = str(int(identifiant_max))


### on va utiliser ce que l on a fait avant pour traiter le texte (expression apres expression, et paragraphe apres paragraphe)

compteur_affichage = 1
for argument_form in list_argument_form :
	for argument_lemma in list_argument_lemma :
		for argument_upostag in list_argument_upostag :
			for argument_deprel in list_argument_deprel :
				for argument_order in list_argument_order :
					time_debut = time.time()
					if not (argument_form or argument_lemma) :
						continue
					nom_methode_verification = ""
					if argument_form :
						nom_methode_verification += "form_"
					if argument_lemma :
						nom_methode_verification += "lemma_"
					if argument_upostag :
						nom_methode_verification += "upostag_"
					if argument_deprel :
						nom_methode_verification += "deprel_"
					if argument_order :
						nom_methode_verification += "order_"											
					nom_methode_verification = nom_methode_verification[:-1]
					print(str(compteur_affichage) + '/' + identifiant_max + ' : ' + nom_methode_verification, file=os.sys.stderr)
					compteur_affichage += 1
					blind(texte_entre_initial) # on remet a zero le text (au niveau des annotations)
					for paragraphe_TokenList in texte_entre :
						#print(str(texte_entre.index(paragraphe_TokenList) + 1) + '/' + str(len(texte_entre)), file=os.sys.stderr) # faire tous les % et indiquer le numero de la combinaison
						remplace_non_expression(paragraphe_TokenList)
						compteur = 1
						for expression in list_expression :
							list_combinaison = creation_list_combinaison(expression, paragraphe_TokenList)
							combinaison = objet_baseline.Combinaison(list_combinaison)
							while combinaison.canContinue() :
								temp_combinaison = []
								compteur_combinaison = 0
								for i in combinaison.getValeur() :
									temp_combinaison.append(list_combinaison[compteur_combinaison][i])
									compteur_combinaison += 1
								combinaison.next()
								if methode_verification_supplementaire(expression, temp_combinaison, argument_order, argument_deprel):
									min_id = temp_combinaison[0].get('id')
									for mot_combinaison in temp_combinaison[1:] :
										if mot_combinaison.get('id') < min_id :
											min_id = mot_combinaison.get('id')
									for mot_combinaison in temp_combinaison :
										if mot_combinaison.get('PARSEME:MWE') == '*' :
											mot_combinaison['PARSEME:MWE'] = str(compteur) + ((':' + expression.getTag()) if mot_combinaison.get('id') == min_id else '')
										else :
											mot_combinaison['PARSEME:MWE'] += ';' + str(compteur) + ((':' + expression.getTag()) if mot_combinaison.get('id') == min_id else '')
									compteur += 1
					with open("baseline/temp_resultat/dev_" + nom_methode_verification + ".txt", 'w') as mon_fichier :
						for paragraphe_TokenList in texte_entre_initial :
							mon_fichier.write(paragraphe_TokenList.serialize())
					os.system("echo " + nom_methode_verification + " > baseline/temp_resultat/scoredev_" + nom_methode_verification + ".txt")
					os.system("echo " + time_temp + " >> baseline/temp_resultat/scoredev_" + nom_methode_verification + ".txt")
					os.system("./baseline/bin/evaluate.py --gold " + parser.parse_args().dev + " --pred baseline/temp_resultat/dev_" + nom_methode_verification + ".txt --train " + parser.parse_args().train + " >> baseline/temp_resultat/scoredev_" + nom_methode_verification + ".txt")
					time_temp = str(round(time.time() - time_debut))
					print(time_temp, file=os.sys.stderr)


### on va chercher la meilleur baseline, d apres ses resultats sur la F-mesure MWE-based
os.system("head -5 baseline/temp_resultat/scoredev_* > baseline/temp_resultat/compilation_resultat")
temp = ''
with open("baseline/temp_resultat/compilation_resultat", 'r') as mon_fichier :
	for ligne in mon_fichier :
		temp += ligne
temp = temp.split('\n\n')

list_resultat = []
for i in temp :
	i = i.split("\n")
	code_lexique = i[1]
	F_mesure = i[4].split('=')[5]
	list_resultat.append([code_lexique,F_mesure])
list_resultat.sort(key=lambda a : a[1], reverse=True)

print(list_resultat[0][0], file=os.sys.stderr)
os.system('echo ' + list_resultat[0][0])
os.system('echo ')
os.system('cat baseline/temp_resultat/lexique.txt')
