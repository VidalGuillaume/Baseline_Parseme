import os

### Permet de representer un mot (appartenant a une expression)
class ExpressionWord :
	information_simple = ['id', 'lemma', 'head']
	information_complexe = [ 'form', 'upostag',  'deprel']
	def __init__(self, mot) :
		self.dict = dict()
		if isinstance(mot, list) :
			self.dict['id'] = mot[0]
			self.dict['form'] = mot[1].split(';')
			self.dict['lemma'] = mot[2]
			self.dict['upostag'] = mot[3].split(';')
			self.dict['head'] = mot[4]
			self.dict['deprel'] = mot[5].split(';')
		else :
			for i in self.information_simple :
				self.dict[i] = mot[i]
			for i in self.information_complexe :
				self.dict[i] = [mot[i]]
			self.dict['form'] = [self.dict['form'][0].lower().replace("-","")]
	def get(self, key) :
		return self.dict.get(key)
	def set (self, key, value) :
		self.dict[key] = value
	def toString(self) :
		resultat = self.dict['id'] + '\t'
		for j in self.dict['form'] :
			resultat += j + ';'
		resultat = resultat[:-1] + '\t'
		resultat += self.dict['lemma'] + '\t'
		for j in self.dict['upostag'] :
			resultat += j + ';'
		resultat = resultat[:-1] + '\t'
		resultat += self.dict['head'] + '\t'
		for j in self.dict['deprel'] :
			resultat += j + ';'
		return resultat[:-1]
	def semi_equals(self, other) :
		for i in self.information_simple :
			if self.dict[i] != other.dict[i] :
				return False
		return True
	def fusion(self, other) :
		for i in self.information_complexe :
			if other.dict[i] == ['_'] :
				continue
			for j in other.dict[i] :
				if not j in self.dict[i] :
					if self.dict[i] == ['_'] :
						self.dict[i] = [j]
					else :
						self.dict[i].append(j)


### Classe permettant de representer une expression (qui est constitue d une liste mot)
class ExpressionComplete :
	def __init__(self) : # permet d initialise une expression vide (ne contenant aucun mot)
		self.list_word = []
		self.order = []
	def add(self, mot) : # permet d ajouter un mot dans l expression
		self.list_word.append(mot)
	def get(self, x) : # permet d acceder a un mot de l expression (grace a son indice dans la liste)
		return self.list_word[x]
	def toString(self) : # permet d obtenir l expression comme un succession de mot sous forme de string, utilise pour generer le lexique
		resultat = ""
		for i in self.order :
			resultat += i + '|'
		resultat = resultat[:-1] + '\n'
		for i in self.list_word :
			resultat += i.toString() + '\n'
		return resultat
	def length(self) : # retourne le nombre de mot que contient l expression
		return len(self.list_word)
	def getListWord(self) : # retourne la liste des mot que contient l expression
		return self.list_word
	def semi_equals(self, other) : # on test l egalite avec other qui est un autre objet de type ExpressionComplete
		if self.length() != other.length() :
			return False
		for i in range(self.length()) :
			if not self.get(i).semi_equals(other.get(i)) :
				return False
		return True
	def sort(self) :
		self.list_word.sort(key = lambda a : a.get('lemma'))
	def getOrder(self) :
		return self.order
	def addOrder(self, order) :
		if not order in self.order :
			self.order.append(order)
	def setOrder(self, order) :
		self.order = order
	def fusion(self, other) :
		for i in range(self.length()) :
			self.get(i).fusion(other.get(i))
		if not other.order[0] in self.order :
			self.order.append(other.order[0])


### Classe permettant de generer toutes les combinaisons possible a partir d un liste donne
class Combinaison :
	def __init__(self, liste_combinaison_possible) : # initialise la 1er combinaisons, ainsi que les valeurs moximales pouvant etre prise par chaque parametre
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
	def getValeur(self) : # retourne la combinaison actuel
		return self.valeur
	def canContinue(self) : # permet de savoir si l on peut tester la combinaison actuel
		return self.can_continue
	def next(self) : # genere la combinaison suivante dans la suite des combinaison possibles
		if self.valeur == self.valeur_max :
			self.can_continue = False
			return
		for i in range(len(self.valeur)-1,-1,-1) :
			self.valeur[i] += 1
			if self.valeur[i] > self.valeur_max[i] :
				self.valeur[i] = 0
				continue
			break




### Methode utilise dans les differents scripts

# a partir d un fichier texte (dont le nom est en argument), retourne le texte brut corrige
def generate_texte_corrige(texte, blind=False) :
	temp = ""
	with open(str(texte), 'r') as mon_fichier:
		for ligne in mon_fichier :
			if ligne[0] == '#' :
				if ligne != "# newdoc\n" and ligne != "# newpar\n" :
					temp += ligne
				elif ligne == "# newdoc\n" :
					temp += "# newdoc id = 0\n"
				elif ligne == "# newpar\n" :
					temp += "# newpar id = 0\n"
				else :
					temp += "# erreur = 0\n"
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
	return temp



def generate_clef(argument_form, argument_lemma, argument_upostag, argument_deprel, argument_order, argument_distance, parametre_distance_verification) :
	nom_methode_verification = ""
	if argument_form :
		nom_methode_verification += "form_"
	if argument_lemma :
		nom_methode_verification += "lemma_"
	if argument_upostag :
		nom_methode_verification += "upostag_"
	if argument_deprel :
		nom_methode_verification += "deprel_"
	if argument_order :
		nom_methode_verification += "order_"
	if argument_distance :
		nom_methode_verification += "distance-" + parametre_distance_verification[0] +  "_"
	return nom_methode_verification[:-1]



# decompose un texte (qui a subi le parse), en bout plus petit afin que les paragraphe a traite soit plus court pour l algo
def segmentation(texte) :
	resultat = []
	for paragraphe in texte : # on va fragment le texte en morceau (entre 100 et 150 mots) de facon a ce que les paragraphes que seront traite ne soient pas trop long
		if len(paragraphe) >= 100 :
			i = 0
			while len(paragraphe[100*i:]) >= 150 : # on veut eviter que le dernier fragment soit trop court
				resultat.append(paragraphe[100*i:100*(i+1)])
				i += 1
			resultat.append(paragraphe[100*i:])
		else :
			resultat.append(paragraphe)
	return resultat

def getFile() :
	return __file__[:-17]

def create_parametre_distance_verification(parametre_min, parametre_max, parametre_moyenne, parametre_variance) :
	return parametre_moyenne + 3*parametre_variance





class GroupExpression :
	def __init__(self, type_expression, list_expression, list_parametre) :
		self.type_expression = type_expression
		self.list_expression = list_expression
		self.parametre_min = list_parametre[0]
		self.parametre_max = list_parametre[1]
		self.parametre_moyenne = list_parametre[2]
		self.parametre_variance = list_parametre[3]
	def getTypeExpression(self) :
		return self.type_expression
	def getListExpression(self) :
		return self.list_expression
	def getParametreMin(self) :
		return self.parametre_min
	def getParametreMax(self) :
		return self.parametre_max
	def getParametreMoyenne(self) :
		return self.parametre_moyenne
	def getParametreVariance(self) :
		return self.parametre_variance
	def toString(self) :
		resultat = self.type_expression + "\n" + "min=" + str(self.parametre_min) + ";max=" + str(self.parametre_max) + ";ave=" + str(round(self.parametre_moyenne,2)) + ";var=" + str(round(self.parametre_variance,2)) + "\n\n"
		for expression in self.list_expression :
			resultat += expression.toString() + '\n'
		return resultat
	def getDistanceVerification(self) :
		return create_parametre_distance_verification(self.parametre_min, self.parametre_max, self.parametre_moyenne, self.parametre_variance)


class ArgumentSelectionExpression() :
	def __init__(self) :
		self.form = False
		self.lemma = False
		self.upostag = False
		self.deprel = False
		self.order = False
		self.distance = False
		self.distance_verification = ["0",0]
	def getForm(self) :
		return self.form
	def getLemma(self) :
		return self.lemma
	def getUpostag(self) :
		return self.upostag
	def getDeprel(self) :
		return self.deprel
	def getOrder(self) :
		return self.order
	def getDistance(self) :
		return self.distance
	def getDistanceVerification(self) :
		return self.distance_verification

def decode_key(key, parametre_distance_min, parametre_distance_max, parametre_distance_ave, parametre_distance_var) :
	argument_selection_expression = ArgumentSelectionExpression()
	argument_form = False
	argument_lemma = False
	argument_upostag = False
	argument_deprel = False
	argument_order = False
	argument_distance = False
	valeur_parametre_distance_verification = "0"
	for i in key.split('_') :
		if i == 'form' :
			argument_selection_expression.form = True
		elif i == 'lemma' :
			argument_selection_expression.lemma = True
		elif i == 'upostag' :
			argument_selection_expression.upostag = True
		elif i == 'deprel' :
			argument_selection_expression.deprel = True
		elif i == 'order' :
			argument_selection_expression.order = True
		elif i[:9] == 'distance-' :
			argument_selection_expression.distance = True
			i = i.split('-')[1]
			if (i == 'default') or i.isdigit() :
				argument_selection_expression.distance_verification[0] = i
			else :
				print("Warning: parameter for distance: must be an int, for exemple distance-10 or distance-default" , file=os.sys.stderr) # on peut mettre un float mais une expression contient un nombre entier de mot, donc prendre un float serait inutile (arrondi)
		else :
			print("Warning: unknow parameter : " + i, file=os.sys.stderr)
	if argument_selection_expression.distance_verification[0] == "default" :
		argument_selection_expression.distance_verification[1] = create_parametre_distance_verification(parametre_distance_min, parametre_distance_max, parametre_distance_ave, parametre_distance_var)
	else :
		argument_selection_expression.distance_verification[1] = int(argument_selection_expression.distance_verification[0])
	return argument_selection_expression



"""
l objet ExpressionComplete peut poser des problemes dans le cas ou l expression comporte plusieurs mots avec le meme lemma
car lors du trie il sera difficile de les differencier donc cela pourrait entrainer un probleme lors de l identification de ces expressions

decodekey ne donne pas assez d information lorsque on l utilise dans le project_lexicon pour les key relie au type d expression, car il ne dit pas quelques clef de quels lexiques contient une erreur
"""