#! /usr/bin/env python3

from genere_tableau import generate_tableau
import os
import time

time_debut = time.time()

os.system('mkdir -p results_baseline')
print("Debut execution\n", file=os.sys.stderr)

liste_langue_normal = ['BG','DE','EL','ES','EU','FA','FR','HE','HR','HU','IT','PL','PT','RO','SL','TR']
liste_langue_cas_particulier = ['EN','HI','LT']

file = __file__[:-31]

compteur_affichage = 1
affichage = "/" + str(len(liste_langue) + len(liste_langue_cas_particulier)) + " :\n"
for langue in liste_langue +  liste_langue_cas_particulier:
	print(langue + " " + str(compteur_affichage) + affichage, file=os.sys.stderr)
	os.system("mkdir -p results_baseline/" + langue + "_result")
	if langue in  liste_langue_cas_particulier :
		os.system(file + "baseline/annotation.py --train " + file + "corpus/" + langue + "_Corpus/train.cupt --test " + file + "corpus/" + langue + "_Corpus/test.blind.cupt > results_baseline/" + langue + "_result/texte_annote.txt")
	else :
		os.system(file + "baseline/annotation.py --train " + file + "corpus/" + langue + "_Corpus/train.cupt --dev " + file + "corpus/" + langue + "_Corpus/dev.cupt --test " + file + "corpus/" + langue + "_Corpus/test.blind.cupt > results_baseline/" + langue + "_result/texte_annote.txt")
		os.system("mv baseline_result/dev_result results_baseline/" + langue + "_result/dev_result")
		os.system("mv baseline_result/compilation_result.txt results_baseline/" + langue + "_result/compilation_result.txt")
	os.system("mv baseline_result/lexicon.txt results_baseline/" + langue + "_result/lexicon.txt")
	os.system(file + "baseline/bin/evaluate.py --gold " + file + "corpus/" + langue + "_Corpus/test.cupt --pred results_baseline/" + langue + "_result/texte_annote.txt --train " + file + "corpus/" + langue + "_Corpus/train.cupt > results_baseline/" + langue + "_result/evaluation.txt")
	os.system("head -4 results_baseline/" + langue + "_result/evaluation.txt")
	print('\n\n\n', file=os.sys.stderr)
	compteur_affichage += 1

print('Fin execution\n' + str(round(time.time() - time_debut)) + "\n", file=os.sys.stderr) 

print("Generating result graph", file=os.sys.stderr)
generate_tableau(liste_langue)
os.system("mv tableau_resultat.csv results_baseline/tableau_resultat.csv")
