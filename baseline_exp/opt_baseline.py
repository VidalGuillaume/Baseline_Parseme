#! /usr/bin/env python3

import argparse
from conllu import parse
from objet_baseline import generate_texte_corrige, generate_clef, decode_key, segmentation, getFile, create_parametre_distance_verification, Combinaison
from extract_lexicon import extract_lexicon
from project_lexicon import project_lexicon
import os
import time

parser = argparse.ArgumentParser(description="A partir des parametres donnes ainsi que des textes train (et dev), genere un lexique contenant les meilleurs parametres pour pouvoir identifier les expressions dans un texte inconnue")
parser.add_argument("--train", help="texte dans lequel on va relever les expressions", required=True)
parser.add_argument("--dev", help="texte, non obligatoire, permettant de trouver les paramtres optimaux pour identifier les expressions", required=False)
parser.add_argument("--form", help="true ou false, par defaut on testera les deux", required=False)
parser.add_argument("--lemma", help="true ou false, par defaut on testera les deux", required=False)
parser.add_argument("--upostag", help="true ou false, par defaut on testera les deux", required=False)
parser.add_argument("--deprel", help="true ou false, par defaut on testera les deux", required=False)
parser.add_argument("--order", help="true ou false, par defaut on testera les deux", required=False)
parser.add_argument("--distance", help="true ou false, par defaut on testera les deux", required=False)
parser.add_argument("--distance_valeur", help="distance maximale entre les mots de l expression, par defaut on prendra la moyenne plus 3 fois la variance", required=False)
# parser.add_argument("--", help="", required=False) 
# parser.parse_args().train
# parser.parse_args().dev

def blind(texte) :
	for phrase in texte :
		for mot_phrase in phrase :
			mot_phrase['PARSEME:MWE'] = '_'







def opt_baseline(file_texte_dev, file_texte_train, list_expression_type, list_argument_form=[True,False], list_argument_lemma=[True,False], list_argument_upostag=[True,False], list_argument_deprel=[True,False], list_argument_order=[True,False], list_argument_distance=[True,False], parametre_distance_verification=["default",-1], display=True) :
	if display :
		print("Debut optimisation total :\n", file=os.sys.stderr)
	time_debut = time.time()
	os.system("mkdir -p baseline_result baseline_result/dev_result") # -p pour eviter le message d erreur car les dossier peuvent deja avoir ete creer

	dict_opt_key = dict()
	file = getFile()


	###############################################################################################
	if file_texte_dev is None :
		print("Dev is Missing :", file=os.sys.stderr)
		print("Lexicon with default key : lemma_upostag_deprel_order\n", file=os.sys.stderr)
		for expression_type in list_expression_type :
			dict_opt_key[expression_type.getTypeExpression()] = "lemma_upostag_deprel_order" 
		return dict_opt_key
	#################################################################################################



	print("Parse Dev :",file=os.sys.stderr)
	time_temp = time.time()
	texte_dev_initial = parse(generate_texte_corrige(file_texte_dev))
	print(str(round(time.time() - time_temp)) + '\n',file=os.sys.stderr)
	
	texte_dev = segmentation(texte_dev_initial)

	# permettant d avoir ce qui se passe de facon plus precise, en calculant le nombre de methode de traitement qui seront tester
	identifiant_max = 1
	for i in [list_argument_upostag, list_argument_deprel, list_argument_order, list_argument_distance] :
		if len(i) == 2 :
			identifiant_max *= 2
	if (len(list_argument_form) == 2) and (len(list_argument_lemma) == 2) :
		identifiant_max *= 3
	elif ((len(list_argument_form) == 2) and list_argument_lemma[0]) or (list_argument_form[0] and (len(list_argument_lemma) == 2)) :
		identifiant_max *= 2
	affichage_identifiant_max = '/' + str(int(identifiant_max)) + " : "


	for expression_type in list_expression_type :
		print("Debut optimisation : " + expression_type.getTypeExpression() + "\n", file=os.sys.stderr)
		time_debut_combinaison = time.time()
		os.system("mkdir -p baseline_result/dev_result/" + expression_type.getTypeExpression())

		compteur_affichage = 0
		combinaison_parametre = Combinaison([list_argument_form, list_argument_lemma, list_argument_upostag, list_argument_deprel, list_argument_order, list_argument_distance])
		while combinaison_parametre.canContinue() :
			time_debut_combinaison = time.time()
			argument_form = list_argument_form[combinaison_parametre.getValeur()[0]]
			argument_lemma = list_argument_lemma[combinaison_parametre.getValeur()[1]]
			argument_upostag = list_argument_upostag[combinaison_parametre.getValeur()[2]]
			argument_deprel = list_argument_deprel[combinaison_parametre.getValeur()[3]]
			argument_order = list_argument_order[combinaison_parametre.getValeur()[4]]
			argument_distance = list_argument_distance[combinaison_parametre.getValeur()[5]]
			combinaison_parametre.next()
			if not (argument_form or argument_lemma) :
				continue
			compteur_affichage += 1

			clef = generate_clef(argument_form, argument_lemma, argument_upostag, argument_deprel, argument_order, argument_distance, parametre_distance_verification)
			print(str(compteur_affichage) + affichage_identifiant_max + clef, file=os.sys.stderr)
	
			blind(texte_dev)		
			project_lexicon(texte_dev, [[expression_type,decode_key(clef, expression_type.getParametreMin(), expression_type.getParametreMax(), expression_type.getParametreMoyenne(), expression_type.getParametreVariance())]], display=False)

			with open("baseline_result/dev_result/" + expression_type.getTypeExpression() + "/dev_" + clef + ".txt", 'w') as mon_fichier :
				for i in texte_dev_initial :
					mon_fichier.write(i.serialize())
			os.system("echo " + clef + " > baseline_result/dev_result/" + expression_type.getTypeExpression() + "/scoredev_" + clef + ".txt")
			os.system("echo " + str(round(time.time() - time_debut_combinaison)) + " >> baseline_result/dev_result/" + expression_type.getTypeExpression() + "/scoredev_" + clef + ".txt")
		
			os.system(file + "bin/evaluate.py --pred baseline_result/dev_result/" + expression_type.getTypeExpression() + "/dev_" + clef + ".txt --gold " + file_texte_dev + " --train " + file_texte_train + " >> baseline_result/dev_result/" + expression_type.getTypeExpression() + "/scoredev_" + clef + ".txt")
		
			print(str(round(time.time() - time_debut_combinaison)), file=os.sys.stderr)
	
		# cherche la meilleur baseline, d apres ses resultats sur la F-mesure MWE-based
		os.system("head -z baseline_result/dev_result/" + expression_type.getTypeExpression() + "/scoredev* > baseline_result/" + expression_type.getTypeExpression() + "_compilation_result.txt")
		temp = ""
		with open("baseline_result/" + expression_type.getTypeExpression() + "_compilation_result.txt", 'r') as mon_fichier:
			for ligne in mon_fichier :
				temp += ligne
		temp = temp.split('==>')

		compilation_resultat = []
		for i in temp :
			if i == '' :
				continue
			i = i.split('\n\n')
			compilation_resultat.append(i)

		list_resultat = []
		for i in compilation_resultat :
			i = i[0].split('\n')
			clef = i[1]
			F_mesure = i[4].split('=')[5]
			list_resultat.append([clef,F_mesure])
		list_resultat.sort(key=lambda a : a[1], reverse=True)
	
		dict_opt_key[expression_type.getTypeExpression()] = list_resultat[0][0]

		print("\nFin optimisation " + expression_type.getTypeExpression() + " : " + list_resultat[0][0] + '\n' + str(round(time.time() - time_debut_combinaison)) + '\n', file=os.sys.stderr)

	if display :
		print("\nFin optimisation total : \n" + str(round(time.time() - time_debut)), file=os.sys.stderr)
	print("", file=os.sys.stderr)
	
	return dict_opt_key









if __name__ == '__main__' :
	print("Debut optimisation total :\n", file=os.sys.stderr)
	time_debut = time.time()
	os.system("mkdir -p baseline_result baseline_result/dev_result baseline_result/temp_result") # -p pour eviter le message d erreur car les dossier peuvent deja avoir ete creer

	print("Parse Train :",file=os.sys.stderr)
	time_temp = time.time()
	texte_train = parse(generate_texte_corrige(parser.parse_args().train))
	print(str(round(time.time() - time_temp)) + '\n',file=os.sys.stderr)

	list_expression_type = extract_lexicon(texte_train, display=True)

	list_argument_form = [True, False]
	list_argument_lemma = [True, False]
	list_argument_upostag =[True, False]
	list_argument_deprel = [True, False]
	list_argument_order = [True, False]
	list_argument_distance = [True, False]
	parametre_distance_verification = ["default",-1]

	if parser.parse_args().form == 'true' :
		list_argument_form = [True]
	elif parser.parse_args().form == 'false' :
		list_argument_form = [False]
	if parser.parse_args().lemma == 'true' :
		list_argument_lemma = [True]
	elif parser.parse_args().lemma == 'false' :
		list_argument_lemma = [False]
	if not (list_argument_form[0] or list_argument_lemma[0]) :
		print("Erreur: need parameter form or lemma", file=os.sys.stderr)
		os.sys.exit()

	if parser.parse_args().upostag == 'true' :
		list_argument_upostag = [True]
	elif parser.parse_args().upostag == 'false' :
		list_argument_upostag = [False]
	if parser.parse_args().deprel == 'true' :
		list_argument_deprel = [True]
	elif parser.parse_args().deprel == 'false' :
		list_argument_deprel = [False]
	if parser.parse_args().order == 'true' :
		list_argument_order = [True]
	elif parser.parse_args().order == 'false' :
		list_argument_order = [False]
	if parser.parse_args().distance == 'true' :
		list_argument_distance = [True]
	elif parser.parse_args().distance == 'false' :
		list_argument_distance = [False]
	if (not parser.parse_args().distance_valeur is None) and (parser.parse_args().distance_valeur.isdigit()) :
		parametre_distance_verification = [parser.parse_args().distance_valeur, int(parser.parse_args().distance_valeur)]


	dict_opt_key = opt_baseline(parser.parse_args().dev, parser.parse_args().train, list_expression_type, list_argument_form=list_argument_form, list_argument_lemma=list_argument_lemma, list_argument_upostag=list_argument_upostag, list_argument_deprel=list_argument_deprel, list_argument_order=list_argument_order, list_argument_distance=list_argument_distance, parametre_distance_verification=parametre_distance_verification, display=False)

	with open("baseline_result/lexicon.txt", 'w') as mon_fichier :
		for expression_type in list_expression_type :
			mon_fichier.write(dict_opt_key[expression_type.getTypeExpression()] + "\n")
			mon_fichier.write(expression_type.toString() + '\n')

	os.system("cat baseline_result/lexicon.txt")

	print("Fin optimisation total : \n" + str(round(time.time() - time_debut)) + "\n", file=os.sys.stderr)

	
	


"""
pas de message d erreur dans le cas ou la saisi d un parametre est incorrect
"""