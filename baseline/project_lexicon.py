#! /usr/bin/env python3

import argparse
from conllu import parse
import objet_baseline
import os
import time

parser = argparse.ArgumentParser(description="A partir des parametres donnes ainsi que des textes train (et dev), genere un lexique contenant les meilleurs parametres pour pouvoir identifier les expressions dans un texte inconnue")
parser.add_argument("--test", help="texte dans lequel on va annoter les expressions", required=True)
parser.add_argument("--lexicon", help="lexique de mot correspondant aux expressions que l on va chercher dans le text test", required=True)
# parser.parse_args().test
# parser.parse_args().lexicon

print("Texte test :", file=os.sys.stderr)

### on va gerer dans un premier temps le texte test
temp = ""
with open(str(parser.parse_args().test), 'r') as mon_fichier:
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
texte_initial = parse(temp)

boolean = False
for phrase in texte_initial :
	for mot_phrase in phrase :
		if mot_phrase['PARSEME:MWE'] != '_' :
			mot_phrase['PARSEME:MWE'] = '_'
			boolean = True
if boolean :
	print("Erreur: le texte test n est pas blind", file=os.sys.stderr)

texte = []
for paragraphe in texte_initial : # on va fragment le texte en morceau (entre 100 et 150 mots) de facon a ce que les paragraphes que seront traite ne soient pas trop long
	if len(paragraphe) >= 100 :
		i = 0
		while len(paragraphe[100*i:]) >= 150 : # on veut eviter que le dernier fragment soit trop court
			texte.append(paragraphe[100*i:100*(i+1)])
			i += 1
		texte.append(paragraphe[100*i:])
	else :
		texte.append(paragraphe)


### on va gerer le lexique
temp = ""
with open(str(parser.parse_args().lexicon), 'r') as mon_fichier:
	for ligne in mon_fichier :
		temp += ligne
temp = temp.split('\n\n')
parametre = temp[0]
lexique = temp[1:]

argument_form = False
argument_lemma = False
argument_upostag = False
argument_deprel = False
argument_order = False
for i in parametre.split('_') :
	if i == 'form' :
		argument_form = True
	elif i == 'lemma' :
		argument_lemma = True
	elif i == 'upostag' :
		argument_upostag = True
	elif i == 'deprel' :
		argument_deprel = True
	elif i == 'order' :
		argument_order = True
	else :
		print("Erreur: parametre du lexique non reconnu, " + i, file=os.sys.stderr)

liste_expression = []
for expression in lexique :
	liste_expression.append(objet_baseline.ExpressionComplete())
	expression = expression.split("\n")
	liste_expression[-1].setTag(expression[0])
	for mot in expression[1:] :
		mot = mot.split("\t")
		mot = objet_baseline.ExpressionWord(mot)
		liste_expression[-1].add(mot)


### methode utilise lors de la recherche des expressions :

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

def creation_list_combinaison(expression, phrase) :
	resultat = []
	for mot_expression in expression.getListWord() :
		resultat.append([])
		for mot_phrase in phrase :
			if methode_verification(mot_expression, mot_phrase, argument_form, argument_lemma, argument_upostag, argument_deprel) :
				resultat[-1].append(mot_phrase)
	return resultat

def remplace_non_expression(phrase) :
	for mot_phrase in phrase :
		if mot_phrase.get('PARSEME:MWE') == '_' :
			mot_phrase['PARSEME:MWE'] = '*'

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


time_debut = time.time()
for paragraphe_TokenList in texte :
	remplace_non_expression(paragraphe_TokenList)
	compteur = 1
	for expression in liste_expression :
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

for paragraphe_TokenList in texte_initial :
	print(paragraphe_TokenList.serialize()[:-1], file=os.sys.stdout) # [:-1] pour enlever le retour a la ligne afin de ne pas en avoir 2 consecutif (le print faisant deja un retour a la ligne)

print(str(round(time.time() - time_debut)), file=os.sys.stderr)