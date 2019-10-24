#!/usr/bin/env python3

class ExpressionWord :
	information = ['id', 'form', 'lemma', 'upostag', 'head', 'deprel'] # ne prend plus le PARSEME:MWE car il va etre lie a l expression complete sous la forme du tag
	def __init__(self, mot) : # mot sous la forme d une list ou d un collecton.OrderedDict
		self.dict = dict()
		if isinstance(mot, list) :
			for i in range(len(self.information)) :
				self.dict[self.information[i]] = mot[i]
		else :
			for i in range(len(self.information)) :
				self.dict[self.information[i]] = mot.get(self.information[i])
	def get(self, key) :
		return self.dict.get(key)
	def set (self, key, value) :
		self.dict[key] = value
	def toString(self) : # permet d obtenir le mot sous forme de string
		resultat = ""
		for i in range(len(self.information)) :
			resultat += str(self.dict.get(self.information[i])) + '\t'
		return resultat[:-1]
	def equals(self, other) : # on test l egalite avec other qui est un autre objet de type ExpressionWord
		for i in range(len(self.information)) :
			if self.dict[self.information[i]] != other.dict[self.information[i]] :
				return False
		return True
# classe qui stock simplement un mot comme etant un 'form'

class ExpressionComplete :
	def __init__(self) :
		self.list_word = []
		self.tag = ""
	def add(self, mot) : # ou le mot est de la classe ExpressionWord
		self.list_word.append(mot)
	def get(self, x) : # ou x est l entier correspondant dans la liste afin d acceder au mot que l on souhaite
		return self.list_word[x]
	def toString(self) : # permet d obtenir l expression comme un succession de mot sous forme de str
		a = self.tag +'\n'
		for i in self.list_word :
			a += i.toString() + '\n'
		return a
	def length(self) : # retourne le nombre de mot que contient l expression
		return len(self.list_word)
	def getListWord(self) : # retourne la liste des mot que contient l expression
		return self.list_word

	def equals(self, other) : # on test l egalite avec other qui est un autre objet de type ExpressionComplete
		if self.length() != other.length() :
			return False
		for i in range(self.length()) :
			if not self.get(i).equals(other.get(i)) :
				return False
		return True
	def getTag(self) :
		return self.tag
	def setTag(self, tag) :
		self.tag = tag

class Combinaison :
	def __init__(self, liste_combinaison_possible) :
		self.valeur = []
		self.valeur_max = []
		self.can_continue = True
		for i in liste_combinaison_possible :
			self.valeur.append(0)
			self.valeur_max.append(len(i)-1)
			if len(i) == 0 :
				self.can_continue = False
		if self.valeur == [] :
			self.can_continue = False
	def getValeur(self) :
		return self.valeur
	def canContinue(self) : # permet de savoir si l on peut tester la combinaison actuel
		return self.can_continue
	def next(self) : # genere la combinaison suivante dans la suite des combinaison possible
		if listEquals(self.valeur, self.valeur_max) :
			self.can_continue = False
			return
		for i in range(len(self.valeur)-1,-1,-1) :
			self.valeur[i] += 1
			if self.valeur[i] > self.valeur_max[i] :
				self.valeur[i] = 0
				continue
			break

def listEquals(list1, list2) : # utiliser pour les list d entier, dans la classe Combnaison
	if len(list1) != len(list1) :
		return False
	for i in range(len(list1)) :
		if list1[i] != list2[i] :
			return False
	return True
