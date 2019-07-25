#! /usr/bin/env python3

import argparse
from conllu import parse
from objet_baseline import generate_texte_corrige, segmentation, decode_key, Combinaison, ExpressionComplete, ExpressionWord
from extract_lexicon import extract_lexicon
import os
import time

parser = argparse.ArgumentParser(description="A partir des parametres donnes ainsi que des textes train (et dev), genere un lexique contenant les meilleurs parametres pour pouvoir identifier les expressions dans un texte inconnue")
parser.add_argument("--test", help="texte dans lequel on va annoter les expressions", required=True)
parser.add_argument("--lexicon", help="lexique de mot correspondant aux expressions que l on va chercher dans le text test", required=True)
# parser.parse_args().test
# parser.parse_args().lexicon

### methode utilise lors de la recherche des expressions :
def methode_verification(mot_expression, mot_phrase, argument_form, argument_lemma, argument_upostag, argument_deprel) :
	if not isinstance(mot_phrase['id'], int) :
		return False
	boolean = True
	if argument_form :
		boolean = boolean and (mot_phrase['form'].lower().replace("-","") in mot_expression.get('form'))
	if argument_lemma :
		boolean = boolean and (mot_expression.get('lemma') == mot_phrase['lemma'])
	if argument_upostag :
		boolean = boolean and (mot_phrase['upostag'] in mot_expression.get('upostag'))
	if argument_deprel :
		boolean = boolean and ((mot_expression.get('deprel') == ['_']) or (mot_phrase['deprel'] in ['root','ROOT','tri']) or (mot_phrase['deprel'] in mot_expression.get('deprel')))
	return boolean

# premiere etape de la verification ou l on genrer une liste de mot pouvant correspondre au mot de l expression traite
def creation_list_combinaison(expression, phrase, argument_form, argument_lemma, argument_upostag, argument_deprel) :
	resultat = []
	for mot_expression in expression.getListWord() :
		resultat.append([])
		for mot_phrase in phrase :
			if methode_verification(mot_expression, mot_phrase, argument_form, argument_lemma, argument_upostag, argument_deprel) :
				resultat[-1].append(mot_phrase)
	return resultat

# etape de verification afin de savoir si l expression que l on test est correct, d apres les parametres supplementaires utilises
def methode_verification_supplementaire(expression, combinaison, texte, argument_deprel, argument_order, argument_distance, valeur_parametre_distance_verification) :
	for mot in combinaison :
		if combinaison.count(mot) != 1 :
			return False
	if argument_order :
		combinaison.sort(key=lambda a : a['id'])
		temp_order = ""
		for mot in combinaison :
			temp_order += mot['lemma'] + ";"
		if not temp_order[:-1] in expression.getOrder() :
			return False
	if argument_deprel :
		combinaison.sort(key=lambda a : a['lemma'])
		for mot_expression in expression.getListWord() :
			if mot_expression.get('head') != '_' :
				if combinaison[int(mot_expression.get('id'))].get('head') != combinaison[int(mot_expression.get('head'))].get('id') :
					return False
	if argument_distance :
		temp_distance = []
		for mot in combinaison :
			temp_distance.append(mot['id'])
		compteur_distance = 0
		temp_taille_min = min(temp_distance)
		temp_taille_max = max(temp_distance)
		for mot in texte :
			if not isinstance(mot['id'], int) :
				continue
			if (mot['id'] > temp_taille_min) and (mot['id'] < temp_taille_max) :
				if not mot in combinaison :
					compteur_distance += 1
		if compteur_distance > valeur_parametre_distance_verification :
			return False
	return True

# permet de modifier les '_' en '*' pour signifier que le mot n appartient pas a une expression, plutot que 'None'
def remplace_non_expression(phrase) :
	for mot_phrase in phrase :
		if mot_phrase.get('PARSEME:MWE') == '_' :
			mot_phrase['PARSEME:MWE'] = '*'

def generate_expression_id(expression, temp_combinaison) :
	resultat = expression.getTag()
	for mot in temp_combinaison :
		resultat += ';' + str(mot['id'])
	return resultat






def project_lexicon(texte_test, liste_expression, argument_form, argument_lemma, argument_upostag, argument_deprel, argument_order, argument_distance, valeur_parametre_distance_verification, display=True) :
	if display :
		print("Project Lexicon : ", file=os.sys.stderr)
	time_debut = time.time()
	os.system("mkdir -p baseline_result baseline_result/temp_result") # -p pour eviter le message d erreur car les dossier peuvent deja avoir ete creer

	boolean = True
	for phrase in texte_test :
		for mot_phrase in phrase :
			if mot_phrase['PARSEME:MWE'] != '_' :
				mot_phrase['PARSEME:MWE'] = '_'
				boolean = False
	if not boolean :
		print("Warning: Test is not blind", file=os.sys.stderr)

	if not (argument_form or argument_lemma or argument_upostag or argument_deprel or argument_order or argument_distance) :
		print("Error: lecixon contains no parameters", file=os.sys.stderr) # si il n y a pas de parametre, alors on ne peut pas rechercher d expression
		os.sys.exit()
	if not (argument_form or argument_lemma) :
		print("Error: lecixon need parameter form or lemma", file=os.sys.stderr) # il faut au moisn le parametre form ou lemma si l on veut faire une recherche correct
		os.sys.exit()

	for paragraphe_TokenList in texte_test :
		sequence_annote = []
		compteur = 1
		for expression in liste_expression :
			list_combinaison = creation_list_combinaison(expression, paragraphe_TokenList, argument_form, argument_lemma, argument_upostag, argument_deprel)
			combinaison = Combinaison(list_combinaison)
			while combinaison.canContinue() :
				temp_combinaison = []
				compteur_combinaison = 0
				for i in combinaison.getValeur() :
					temp_combinaison.append(list_combinaison[compteur_combinaison][i])
					compteur_combinaison += 1
				combinaison.next()
				if methode_verification_supplementaire(expression, temp_combinaison, paragraphe_TokenList, argument_deprel, argument_order, argument_distance, valeur_parametre_distance_verification) :
					expression_id = generate_expression_id(expression, temp_combinaison)
					if expression_id in sequence_annote :
						continue
					sequence_annote.append(expression_id)
					min_id = temp_combinaison[0].get('id')
					for mot_combinaison in temp_combinaison[1:] :
						if mot_combinaison.get('id') < min_id :
							min_id = mot_combinaison.get('id')
					for mot_combinaison in temp_combinaison :
						if mot_combinaison.get('PARSEME:MWE') == '_' :
							mot_combinaison['PARSEME:MWE'] = str(compteur) + ((':' + expression.getTag()) if mot_combinaison.get('id') == min_id else '')
						else :
							mot_combinaison['PARSEME:MWE'] += ';' + str(compteur) + ((':' + expression.getTag()) if mot_combinaison.get('id') == min_id else '')
					compteur += 1
		remplace_non_expression(paragraphe_TokenList)
	
	if display :
		print(str(round(time.time() - time_debut)) + "\n", file=os.sys.stderr)










if __name__ == "__main__" :
	print("Project Lexicon : ", file=os.sys.stderr)
	time_debut = time.time()
	os.system("mkdir -p baseline_result baseline_result/temp_result") # -p pour eviter le message d erreur car les dossier peuvent deja avoir ete creer

	temp = ""
	with open(str(parser.parse_args().lexicon), 'r') as mon_fichier:
		for ligne in mon_fichier :
			temp += ligne
	temp = temp.split('\n\n')
	partie_parametre = temp[0].split('\n')
	partie_expression = temp[1:]

	liste_expression = []
	for expression in partie_expression :
		expression = expression.split("\n")
		if len(expression) == 1 :
			continue
		liste_expression.append(ExpressionComplete())
		liste_expression[-1].setTag(expression[0])
		for i in expression[1].split('|') :
			liste_expression[-1].addOrder(i)
		for mot in expression[2:] :
			mot = mot.split("\t")
			mot = ExpressionWord(mot)
			liste_expression[-1].add(mot)

	temp_distance = partie_parametre[1].split(';')
	parametre_distance_min = int(temp_distance[0].split('=')[1])
	parametre_distance_max = int(temp_distance[1].split('=')[1])
	parametre_distance_ave = float(temp_distance[2].split('=')[1])
	parametre_distance_var = float(temp_distance[3].split('=')[1])

	key = partie_parametre[0]
	argument_form, argument_lemma, argument_upostag, argument_deprel, argument_order, argument_distance, valeur_parametre_distance_verification = decode_key(key, parametre_distance_min, parametre_distance_max, parametre_distance_ave, parametre_distance_var)

	texte_test_initial = parse(generate_texte_corrige(parser.parse_args().test))

	texte_test = segmentation(texte_test_initial)

	project_lexicon(texte_test, liste_expression, argument_form, argument_lemma, argument_upostag, argument_deprel, argument_order, argument_distance, valeur_parametre_distance_verification, display=False)

	with open("baseline_result/temp_result/" + key + ".txt", 'w') as mon_fichier :
		for paragraphe_TokenList in texte_test_initial :
			mon_fichier.write(paragraphe_TokenList.serialize())

	os.system("cat baseline_result/temp_result/" + key + ".txt")

	print(str(round(time.time() - time_debut)) + "\n", file=os.sys.stderr)



"""
dans le cas ou la key comporte plusieurs fois une meme information, seul la derniere est prise en compte, donc si on met : distance=default_distance=10, alors ce sera 10 et non default qui sera pris en compte

mettre comme argument lex au lieu de lexicon ?
"""
