#! /usr/bin/env python3

import csv


resultat_baseline = dict()

"""
import os
os.system("ls resultats/ > resultats/temp")
temp = ''
with open("resultats/temp",'r') as file :
	for ligne in file :
		temp += ligne
temp = temp.split('\n')
liste_langue = []
for i in temp :
	if i[2:] == '_resultat' :
		liste_langue.append(i[:2])
"""

#liste_langue = ['BG','DE','EL','ES','EU','FA','FR','HE','HR','HU','IT','PL','PT','RO','SL','TR']
#liste_langue = ["Yolo","Yolo0"]

liste_category = ['Global','Seen-in-train','Variant-of-train','Identical-to-train']

def dict_mesure() :
	resultat = dict()
	resultat['Precision'] = '????'
	resultat['Rappel'] = '????'
	resultat['F-mesure'] = '????'
	return resultat


def dict_category() :
	resultat = dict()

	### Global evaluation
	resultat["Global"] = dict()
	resultat["Global"]['MWE-based'] = dict_mesure()
	resultat["Global"]['Tok-based'] = dict_mesure()

	### Wheter seen in train
	resultat["Seen-in-train"] = dict_mesure()

	### Wheter identical to train
	resultat["Variant-of-train"] = dict_mesure()
	resultat["Identical-to-train"] = dict_mesure()

	### Rank
	resultat["Rank"] = '????'

	return resultat
	
def extract_PRF(texte) :
	texte = texte.split(' ')
	return   # P , R , F


def implement_dict_evaluation(evaluation, liste_langue, langue) :
	evaluation = evaluation.split('\n\n')
	temp = []
	for i in evaluation :
		temp.append(i.split('\n'))
	nom_baseline = temp[0][1]
	
	if not nom_baseline in resultat_baseline :
		resultat_baseline[nom_baseline] = dict()
		for i in liste_langue :
			resultat_baseline[nom_baseline][i] = dict_category()

	global_mwe_based = temp[0][4].split(' ')
	p,r,f = global_mwe_based[2].split('=')[2] , global_mwe_based[3].split('=')[2] , global_mwe_based[4].split('=')[1]
	resultat_baseline[nom_baseline][langue]['Global']['MWE-based']['Precision'] = p
	resultat_baseline[nom_baseline][langue]['Global']['MWE-based']['Rappel'] = r
	resultat_baseline[nom_baseline][langue]['Global']['MWE-based']['F-mesure'] = f

	global_tok_based = temp[0][5].split(' ')
	p,r,f = global_tok_based[2].split('=')[2] , global_tok_based[3].split('=')[2] , global_tok_based[4].split('=')[1]
	resultat_baseline[nom_baseline][langue]['Global']['Tok-based']['Precision'] = p
	resultat_baseline[nom_baseline][langue]['Global']['Tok-based']['Rappel'] = r
	resultat_baseline[nom_baseline][langue]['Global']['Tok-based']['F-mesure'] = f

	seen_in_train = temp[4][2].split(' ')
	p,r,f = seen_in_train[3].split('=')[2] , seen_in_train[4].split('=')[2] , seen_in_train[5].split('=')[1]
	resultat_baseline[nom_baseline][langue]['Seen-in-train']['Precision'] = p
	resultat_baseline[nom_baseline][langue]['Seen-in-train']['Rappel'] = r
	resultat_baseline[nom_baseline][langue]['Seen-in-train']['F-mesure'] = f

	variant_of_train = temp[5][2].split(' ')
	p,r,f = variant_of_train[3].split('=')[2] , variant_of_train[4].split('=')[2] , variant_of_train[5].split('=')[1]
	resultat_baseline[nom_baseline][langue]['Variant-of-train']['Precision'] = p
	resultat_baseline[nom_baseline][langue]['Variant-of-train']['Rappel'] = r
	resultat_baseline[nom_baseline][langue]['Variant-of-train']['F-mesure'] = f

	identical_to_train = temp[5][4].split(' ')
	p,r,f = identical_to_train[3].split('=')[2] , identical_to_train[4].split('=')[2] , identical_to_train[5].split('=')[1]
	resultat_baseline[nom_baseline][langue]['Identical-to-train']['Precision'] = p
	resultat_baseline[nom_baseline][langue]['Identical-to-train']['Rappel'] = r
	resultat_baseline[nom_baseline][langue]['Identical-to-train']['F-mesure'] = f



def saut_ligne(tsv_writer, nombre) :
	for i in range(nombre) :
		tsv_writer.writerow([])



def generate_tableau(liste_langue) :
	for langue in liste_langue :
		temp = ""
		with open("results_baseline/" + langue + "_result/compilation_result.txt",'r') as file :
			for ligne in file :
				temp += ligne
		list_evaluation = temp.split('\n\n\n')
		for evaluation in list_evaluation :
			implement_dict_evaluation(evaluation, liste_langue, langue)


	with open('tableau_resultat.csv','w') as out_file :
		tsv_writer = csv.writer(out_file, dialect="excel", delimiter=";")
		#tableau(tsv_writer, "Global : F-mesure", ["Global","MWE-based","F-mesure"])
		#tableau_bis(tsv_writer, "Global : Precision + Rappel", [["Precision",["Global","MWE-based","Precision"]],["Rappel",["Global","MWE-based","Rappel"]]])
	
		### Global
		tsv_writer.writerow(["Result : Global"])
		saut_ligne(tsv_writer, 3)

		tsv_writer.writerow(["Global : F-mesure"])
		tsv_writer.writerow([""] + (liste_langue))
		for nom_baseline in resultat_baseline.keys() :
			temp = [nom_baseline]
			for langue in liste_langue :
				temp.append(resultat_baseline[nom_baseline][langue]["Global"]['MWE-based']['F-mesure'])
			tsv_writer.writerow(temp)
		saut_ligne(tsv_writer, 5)

		tsv_writer.writerow(["Global : Precision"])
		tsv_writer.writerow([""] + (liste_langue))
		for nom_baseline in resultat_baseline.keys() :
			temp = [nom_baseline]
			for langue in liste_langue :
				temp.append(resultat_baseline[nom_baseline][langue]["Global"]['MWE-based']['Precision'])
			tsv_writer.writerow(temp)
		saut_ligne(tsv_writer, 5)
	
		tsv_writer.writerow(["Global : Rappel"])
		tsv_writer.writerow([""] + (liste_langue))
		for nom_baseline in resultat_baseline.keys() :
			temp = [nom_baseline]
			for langue in liste_langue :
				temp.append(resultat_baseline[nom_baseline][langue]["Global"]['MWE-based']['Rappel'])
			tsv_writer.writerow(temp)
		saut_ligne(tsv_writer, 5)

		tsv_writer.writerow(["Global : Precision + Rappel"])
		tsv_writer.writerow(["",""] + (liste_langue))
		for nom_baseline in resultat_baseline.keys() :
			temp = [nom_baseline,"Precision"]
			temp0 = ["","Rappel"]
			for langue in liste_langue :
				temp.append(resultat_baseline[nom_baseline][langue]["Global"]['MWE-based']['Precision'])
				temp0.append(resultat_baseline[nom_baseline][langue]["Global"]['MWE-based']['Rappel'])
			tsv_writer.writerow(temp)
			tsv_writer.writerow(temp0)
			tsv_writer.writerow([])
		saut_ligne(tsv_writer, 5)

		tsv_writer.writerow(["Global : Precision + Rappel + F-mesure"])
		tsv_writer.writerow(["",""] + (liste_langue))
		for nom_baseline in resultat_baseline.keys() :
			temp = [nom_baseline,"Precision"]
			temp0 = ["","Rappel"]
			temp1 = ["","F-mesure"]
			for langue in liste_langue :
				temp.append(resultat_baseline[nom_baseline][langue]["Global"]['MWE-based']['Precision'])
				temp0.append(resultat_baseline[nom_baseline][langue]["Global"]['MWE-based']['Rappel'])
				temp1.append(resultat_baseline[nom_baseline][langue]["Global"]['MWE-based']['F-mesure'])
			tsv_writer.writerow(temp)			
			tsv_writer.writerow(temp0)		
			tsv_writer.writerow(temp1)
			tsv_writer.writerow([])
		saut_ligne(tsv_writer, 5)



		### Seen in train
		saut_ligne(tsv_writer, 3)
		tsv_writer.writerow(["Result : Seen in train"])
		saut_ligne(tsv_writer, 3)


		tsv_writer.writerow(["Seen in train : F-mesure"])
		tsv_writer.writerow([""] + (liste_langue))
		for nom_baseline in resultat_baseline.keys() :
			temp = [nom_baseline]
			for langue in liste_langue :
				temp.append(resultat_baseline[nom_baseline][langue]["Seen-in-train"]['F-mesure'])
			tsv_writer.writerow(temp)
		saut_ligne(tsv_writer, 5)

		tsv_writer.writerow(["Seen in train : Precision"])
		tsv_writer.writerow([""] + (liste_langue))
		for nom_baseline in resultat_baseline.keys() :
			temp = [nom_baseline]
			for langue in liste_langue :
				temp.append(resultat_baseline[nom_baseline][langue]["Seen-in-train"]['Precision'])
			tsv_writer.writerow(temp)
		saut_ligne(tsv_writer, 5)
	
		tsv_writer.writerow(["Seen in train : Rappel"])
		tsv_writer.writerow([""] + (liste_langue))
		for nom_baseline in resultat_baseline.keys() :
			temp = [nom_baseline]
			for langue in liste_langue :
				temp.append(resultat_baseline[nom_baseline][langue]["Seen-in-train"]['Rappel'])
			tsv_writer.writerow(temp)
		saut_ligne(tsv_writer, 5)

		tsv_writer.writerow(["Seen in train : Precision + Rappel"])
		tsv_writer.writerow(["",""] + (liste_langue))
		for nom_baseline in resultat_baseline.keys() :
			temp = [nom_baseline,"Precision"]
			temp0 = ["","Rappel"]
			for langue in liste_langue :
				temp.append(resultat_baseline[nom_baseline][langue]["Seen-in-train"]['Precision'])
				temp0.append(resultat_baseline[nom_baseline][langue]["Seen-in-train"]['Rappel'])
			tsv_writer.writerow(temp)
			tsv_writer.writerow(temp0)
			tsv_writer.writerow([])
		saut_ligne(tsv_writer, 5)
	
		tsv_writer.writerow(["Seen in train : Precision + Rappel + F-mesure"])
		tsv_writer.writerow(["",""] + (liste_langue))
		for nom_baseline in resultat_baseline.keys() :
			temp = [nom_baseline,"Precision"]
			temp0 = ["","Rappel"]
			temp1 = ["","F-mesure"]
			for langue in liste_langue :
				temp.append(resultat_baseline[nom_baseline][langue]["Seen-in-train"]['Precision'])
				temp0.append(resultat_baseline[nom_baseline][langue]["Seen-in-train"]['Rappel'])
				temp1.append(resultat_baseline[nom_baseline][langue]["Seen-in-train"]['F-mesure'])
			tsv_writer.writerow(temp)			
			tsv_writer.writerow(temp0)		
			tsv_writer.writerow(temp1)
			tsv_writer.writerow([])
		saut_ligne(tsv_writer, 5)

		### Variant of train vs Identical to train
		saut_ligne(tsv_writer, 3)
		tsv_writer.writerow(["Result : Variant of train vs Identical to train"])
		saut_ligne(tsv_writer, 3)

		tsv_writer.writerow(["Variant of train vs Identical to train : Precision + Rappel + F-mesure"])
		tsv_writer.writerow(["","",""] + (liste_langue))
		for nom_baseline in resultat_baseline.keys() :
			temp = [nom_baseline,"Variant","Precision"]
			temp0 = ["","","Rappel"]
			temp1 = ["","","F-mesure"]
			temp2 = ["","Identical","Precision"]
			temp3 = ["","","Rappel"]
			temp4 = ["","","F-mesure"]
			for langue in liste_langue :
				temp.append(resultat_baseline[nom_baseline][langue]["Variant-of-train"]['Precision'])
				temp0.append(resultat_baseline[nom_baseline][langue]["Variant-of-train"]['Rappel'])
				temp1.append(resultat_baseline[nom_baseline][langue]["Variant-of-train"]['F-mesure'])
				temp2.append(resultat_baseline[nom_baseline][langue]["Identical-to-train"]['Precision'])
				temp3.append(resultat_baseline[nom_baseline][langue]["Identical-to-train"]['Rappel'])
				temp4.append(resultat_baseline[nom_baseline][langue]["Identical-to-train"]['F-mesure'])
			tsv_writer.writerow(temp)
			tsv_writer.writerow(temp0)
			tsv_writer.writerow(temp1)
			tsv_writer.writerow([])
			tsv_writer.writerow(temp2)
			tsv_writer.writerow(temp3)
			tsv_writer.writerow(temp4)
			tsv_writer.writerow([])

		saut_ligne(tsv_writer, 8)
		tsv_writer.writerow(["Rank : Global MWE-based"])
		tsv_writer.writerow([""] + (liste_langue))
		for langue in liste_langue :
			list_rank = []
			for nom_baseline in resultat_baseline.keys() :
				list_rank.append([nom_baseline,resultat_baseline[nom_baseline][langue]["Global"]['MWE-based']['F-mesure']])
			list_rank.sort(key=lambda a : a[1], reverse=True)
			compteur = 1
			for i in list_rank :
				resultat_baseline[i[0]][langue]["Rank"] = str(compteur)
				compteur += 1

		for nom_baseline in resultat_baseline.keys() :
			temp = [nom_baseline]
			for langue in liste_langue :
				temp.append(resultat_baseline[nom_baseline][langue]["Rank"])
			tsv_writer.writerow(temp)







"""
def tableau(tsv_writer, nom_tableau, combinaison) :
	tsv_writer.writerow([nom_tableau])
	tsv_writer.writerow([""] + liste_langue)
	for nom_baseline in resultat_baseline.keys() :
		temp = [nom_baseline]
		for langue in liste_langue :
			temp0 = resultat_baseline[nom_baseline][langue]
			for i in combinaison :
				temp0 = temp0[i]
			temp.append(temp0)
		tsv_writer.writerow(temp)
	saut_ligne(tsv_writer,5)

def tableau_bis(tsv_writer, nom_tableau, list_combinaison) :
	tsv_writer.writerow([nom_tableau])
	tsv_writer.writerow([""]*len(list_combinaison) + liste_langue)
	for nom_baseline in resultat_baseline.keys() :
		list_temp = []
		boolean = True
		for combinaison in list_combinaison :
			if boolean :
				list_temp.append([nom_baseline] + [combinaison[0]])
				boolean = False
			else :
				list_temp.append([""] + [combinaison[0]])

		for langue in liste_langue :
			for i in range(len(list_temp)) :
				temp0 = resultat_baseline[nom_baseline][langue]
				for j in list_combinaison[i][1] :
					temp0 = temp0[j]
				list_temp[i].append(temp0)
		for temp in list_temp :
			tsv_writer.writerow(temp)
	saut_ligne(tsv_writer,5)
"""


"""
plusieurs tableau separer par environ 5 lignes vides
1er : F-mesure pour le global (MWE-Based)
2er : Precision et Rappel pour le global (MWE-Based)
3em : Precision, Rappel et F-mesure pour les seen (MWE-Based)
4em : Precision, Rappel et F-mesure pour les Variant vs Identical (MWE-Based)
5em : Rang de la baseline selon la langue
"""

"""
dict.0 dont la clef est le nom de la baseline, et comme valeur un dict.1
les clef de dict.1 sont le nom des langues, et les valeurs sont des dict.2
les clefs de dict.2 sont (Global, per category, seen in train..) avec comme valeur des dict.3 contenant (Mwe-based...)
les clef des dict.3 sont les P , R et F mesure avec comme valeur des entier (str avec %)
"""

"""
Ne prend pas en compte les 'Per-category', 'MWE-continuity'et 'Number-of-tokens'
"""
