#! /usr/bin/env python3

import argparse
from conllu import parse
from objet_baseline import generate_texte_corrige, ExpressionComplete, ExpressionWord
import os
import time

parser = argparse.ArgumentParser(description="A partir des parametres donnes ainsi que des textes train (et dev), genere un lexique contenant les meilleurs parametres pour pouvoir identifier les expressions dans un texte inconnue")
parser.add_argument("--train", help="texte dans lequel on va relever les expressions", required=True)
# parser.parse_args().train


def extract_lexicon(texte_train, display=True) :
	if display :
		print("Extract Lexicon :", file=os.sys.stderr)
	time_debut = time.time()
	os.system("mkdir -p baseline_result baseline_result/temp_result") # -p pour eviter le message d erreur car les dossier peuvent deja avoir ete creer
	
	list_expression = []
	list_donne = []
	for paragraphe_TokenList in texte_train :
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
			expression_complete = ExpressionComplete()
			expression_complete.setTag(expression[0])
			
			taille_expression = []
			order = ""
			for mot in expression[1:] :
				mot_expression = ExpressionWord(mot)
				expression_complete.add(mot_expression)
				taille_expression.append(mot['id'])
				order += mot['lemma'] + ';'
			expression_complete.sort()
			expression_complete.addOrder(order[:-1])
		
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
					mot.set('deprel', ['_'])

			# on met en place un anti doublon brut afin de reduire leur nombre
			boolean = True
			for i in list_expression :
				if i.semi_equals(expression_complete) :
					boolean = False
					i.fusion(expression_complete)
			if boolean :
				list_expression.append(expression_complete)
			
			temp_compteur = 0
			temp_taille_min = min(taille_expression)
			temp_taille_max = max(taille_expression)
			for mot in paragraphe_TokenList :
				if not isinstance(mot['id'], int) :
					continue
				if (mot['id'] > temp_taille_min) and (mot['id'] < temp_taille_max) :
					if not mot in expression :
						temp_compteur += 1
			list_donne.append(temp_compteur)

	if len(list_donne) == 0 :
		parametre_min = 0
		parametre_max = 0
		parametre_moyenne = 0
		parametre_variance = 0
	else :
		parametre_min = min(list_donne)
		parametre_max = max(list_donne)
		parametre_moyenne = 0 # average
		for i in list_donne :
			parametre_moyenne += i
		parametre_moyenne /= len(list_donne)
		parametre_variance = 0 # standard deviation
		for i in list_donne :
			parametre_variance += (i - parametre_moyenne)**2
		parametre_variance /= len(list_donne)

	if display :
		print(str(round(time.time() - time_debut)) + '\n', file=os.sys.stderr)

	return list_expression, [parametre_min, parametre_max, parametre_moyenne, parametre_variance] # pour le opt_lexicon


if __name__ == "__main__" :
	print("Extract Lexicon :", file=os.sys.stderr)
	time_debut = time.time()
	os.system("mkdir -p baseline_result baseline_result/temp_result") # -p pour eviter le message d erreur car les dossier peuvent deja avoir ete creer
	
	list_expression, [parametre_min, parametre_max, parametre_moyenne, parametre_variance] = extract_lexicon(parse(generate_texte_corrige(parser.parse_args().train)), display=False)
	
	with open("baseline_result/temp_result/lexicon.txt", 'w') as mon_fichier :
		mon_fichier.write("key\n")
		mon_fichier.write("min=" + str(parametre_min) + ";max=" + str(parametre_max) + ";ave=" + str(round(parametre_moyenne,2)) + ";var=" + str(round(parametre_variance,2)) + "\n\n")
		for expression in list_expression :
			mon_fichier.write(expression.toString() + '\n')
	
	os.system("cat baseline_result/temp_result/lexicon.txt")

	print(str(round(time.time() - time_debut)) + '\n', file=os.sys.stderr)
