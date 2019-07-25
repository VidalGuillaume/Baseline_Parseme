#! /usr/bin/env python3

import argparse
from objet_baseline import decode_key, segmentation, generate_texte_corrige, ExpressionWord, ExpressionComplete
from extract_lexicon import extract_lexicon
from opt_baseline import opt_baseline
from project_lexicon import project_lexicon
from conllu import parse
import os
import time

parser = argparse.ArgumentParser(description="")
parser.add_argument("--train", help="texte dans lequel on va relever les expressions", required=True)
parser.add_argument("--dev", help="texte, non obligatoire, permettant de trouver les paramtres optimaux pour identifier les expressions", required=False)
parser.add_argument("--test", help="texte dans lequel on va annoter les expressions", required=True)
parser.add_argument("--key", help="clef facultative, dans le cas ou l on veut faire un teste avec une methode en particulier", required=False)
# parser.parse_args().train
# parser.parse_args().dev
# parser.parse_args().test
# parser.parse_args().key

time_debut = time.time()

os.system("mkdir -p baseline_result baseline_result/temp_result")

print("Parse Train :",file=os.sys.stderr)
time_temp = time.time()
texte_train = parse(generate_texte_corrige(parser.parse_args().train))
print(str(round(time.time() - time_temp)) + '\n',file=os.sys.stderr)

list_expression, [parametre_min, parametre_max, parametre_moyenne, parametre_variance] = extract_lexicon(texte_train, display=True)
parametre_moyenne = round(parametre_moyenne,2)
parametre_variance = round(parametre_variance,2)

with open("baseline_result/temp_result/lexicon.txt", 'w') as mon_fichier :
	mon_fichier.write("key\n")
	mon_fichier.write("min=" + str(parametre_min) + ";max=" + str(parametre_max) + ";ave=" + str(parametre_moyenne) + ";var=" + str(parametre_variance) + "\n\n")
	for expression in list_expression :
		mon_fichier.write(expression.toString() + '\n')

parametre_distance_verification = ["default", parametre_moyenne + 3*parametre_variance]

key = opt_baseline(parser.parse_args().dev, parser.parse_args().train, list_expression, parametre_distance_verification=parametre_distance_verification, display=True) if parser.parse_args().key is None else parser.parse_args().key
print("key opt : " + key + "\n", file=os.sys.stderr)

argument_form, argument_lemma, argument_upostag, argument_deprel, argument_order, argument_distance, valeur_parametre_distance_verification = decode_key(key, parametre_min, parametre_max, parametre_moyenne, parametre_variance)

os.system("echo " + key + " > baseline_result/lexicon.txt")
os.system("tail -n +2 baseline_result/temp_result/lexicon.txt >> baseline_result/lexicon.txt")

print("Parse Test :",file=os.sys.stderr)
time_temp = time.time()
texte_test_initial = parse(generate_texte_corrige(parser.parse_args().test))
print(str(round(time.time() - time_temp)) + "\n",file=os.sys.stderr)

texte_test = segmentation(texte_test_initial)

project_lexicon(texte_test, list_expression, argument_form, argument_lemma, argument_upostag, argument_deprel, argument_order, argument_distance, valeur_parametre_distance_verification, display=True)

with open("baseline_result/texte_annote.txt", 'w') as mon_fichier :
	for i in texte_test_initial :
		mon_fichier.write(i.serialize())

os.system("cat baseline_result/texte_annote.txt")

print("Time :\n" + str(round(time.time() - time_debut)) + "\n", file=os.sys.stderr)


"""
Ajouter les notifications des temps de parse dans les autres scripts
"""