#! /usr/bin/env python3

import argparse
from objet_baseline import decode_key, segmentation, generate_texte_corrige, create_parametre_distance_verification, ExpressionWord, ExpressionComplete
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

list_expression_type = extract_lexicon(texte_train, display=True)

if parser.parse_args().key is None :
	dict_opt_key = opt_baseline(parser.parse_args().dev, parser.parse_args().train, list_expression_type, display=True)
else :
	dict_opt_key = dict()
	for expression_type in list_expression_type :
		dict_opt_key[expression_type.getTypeExpression()] = parser.parse_args().key

with open("baseline_result/lexicon.txt", 'w') as mon_fichier :
	for expression_type in list_expression_type :
		mon_fichier.write(dict_opt_key[expression_type.getTypeExpression()] + "\n")
		mon_fichier.write(expression_type.toString() + '\n')

print("Parse Test :",file=os.sys.stderr)
time_temp = time.time()
texte_test_initial = parse(generate_texte_corrige(parser.parse_args().test))
print(str(round(time.time() - time_temp)) + "\n",file=os.sys.stderr)

texte_test = segmentation(texte_test_initial)

list_expression_type_argument = []
for expression_type in list_expression_type :
	list_expression_type_argument.append([expression_type, decode_key(dict_opt_key[expression_type.getTypeExpression()],expression_type.getParametreMin(),expression_type.getParametreMax(),expression_type.getParametreMoyenne(),expression_type.getParametreVariance())])

project_lexicon(texte_test, list_expression_type_argument, display=True)

with open("baseline_result/texte_annote.txt", 'w') as mon_fichier :
	for i in texte_test_initial :
		mon_fichier.write(i.serialize())

os.system("cat baseline_result/texte_annote.txt")

print("Time :\n" + str(round(time.time() - time_debut)) + "\n", file=os.sys.stderr)


"""
Ajouter les notifications des temps de parse dans les autres scripts
"""