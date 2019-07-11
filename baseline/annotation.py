#! /usr/bin/env python3

import argparse
import os
import time

parser = argparse.ArgumentParser(description="A partir des parametres donnes ainsi que des textes train (et dev), genere un lexique contenant les meilleurs parametres pour pouvoir identifier les expressions dans un texte inconnue")
parser.add_argument("--train", help="texte dans lequel on va relever les expressions", required=True)
parser.add_argument("--dev", help="texte, non obligatoire, permettant de trouver les paramtres optimaux pour identifier les expressions", required=False)
parser.add_argument("--test", help="texte dans lequel on va annoter les expressions", required=True)
parser.add_argument("--affichage", help="false : pour ne pas avoir le texte qui apparait, et le recupere dans le dossier baseline/resultat/texte_annote.txt", required=False)
# parser.parse_args().train
# parser.parse_args().dev
# parser.parse_args().test
# parser.parse_args().affichage

time_debut = time.time()

os.system("mkdir baseline/resultat")
os.system("rm baseline/resultat/*")

if parser.parse_args().dev is None :
	os.system("./baseline/opt_baseline.py --train " + parser.parse_args().train + " --all true > baseline/resultat/lexique.txt")	
else :
	os.system("./baseline/opt_baseline.py --train " + parser.parse_args().train + " --dev " + parser.parse_args().dev + " --all true > baseline/resultat/lexique.txt")

os.system("./baseline/project_lexicon.py --test " + parser.parse_args().test + " --lexicon baseline/resultat/lexique.txt > baseline/resultat/texte_annote.txt")

if parser.parse_args().affichage != 'false' :
	os.system("cat baseline/resultat/texte_annote.txt")

print("Duree total du traitement :\n" + str(round(time.time() - time_debut)), file=os.sys.stderr)