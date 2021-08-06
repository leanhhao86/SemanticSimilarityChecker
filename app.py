# Compare two sentences using semantic analysis
# Dependency token list: https://universaldependencies.org/docs/en/dep/
# POS tag list: https://universaldependencies.org/docs/en/pos/
# Referenced paper: Mukherjee, I., Kumar, B., Singh, S. and Sharma, K., 2018. Plagiarism detection based on semantic analysis. International Journal of Knowledge and Learning, 12(3), pp.242-254.
# This checks for sentence similarity based on Object-Action model


import spacy
from spacy.symbols import *
from nltk.corpus import wordnet
from itertools import product


# Initialize
nlp = spacy.load('en_core_web_sm')
ACCEPTED_RATE = 0.8 # accepted rate for wup's similarity (word-word)


def sentence_preprocess(text):
	'''
	Process a sentence into Object-Action model
	'''
	doc = nlp(text)
	# list of possible pos
	pos_list = [ADJ, ADV, NOUN, NUM, PRON, PROPN, VERB]

	# Tokenization & Stopword Removal
	print(text)
	doc_token_list = []
	for token in doc:
		if nlp.vocab[token.lemma_].is_stop == False and token.pos in pos_list: 
			doc_token_list.append(token)
			# print(token.lemma_, token.pos_, token.dep_)


	# Build Object-Action model
	# Approach: get token with susceptible dependency

	dep_list = [nsubj, nsubjpass] # susceptible dependencies
	doc_res = {}
	doc_res["Action"] = set()
	doc_res["Object"] = set()

	# print("token list: ", doc_token_list)
	for token in doc_token_list:
		if token.dep in dep_list:
			doc_res["Object"].add(token.lemma_.lower())

		else:
			doc_res["Action"].add(token.lemma_.lower())



	# print(doc_res)
	return doc_res

def object_match(obj1, obj2):
	'''	
	Check if Objects of two sentences match by finding the mutual Object
	'''
	for word1 in obj1:
		synset1 = wordnet.synsets(word1)
		
		for word2 in obj2:
			synset2 = wordnet.synsets(word2)
			
			for sense1, sense2 in product(synset1, synset2):
				t = wordnet.wup_similarity(sense1, sense2)
				if t != None and t >= ACCEPTED_RATE:
					# If there is one possible match
					return True
		
	return False

def sentence_similarity(text1, text2):
	'''
	Perform full similarity check of two sentences and return similarity percentage
	'''
	doc_res1 = sentence_preprocess(text1)
	doc_res2 = sentence_preprocess(text2)

	# if their objects match, proceed to compare their actions
	if object_match(doc_res1["Object"], doc_res2["Object"]):
		doc1_actions = doc_res1["Action"]
		doc2_actions = doc_res2["Action"]
		sentence_sim = []

		for word1 in doc1_actions:
			word_sim = []
			synset1 = wordnet.synsets(word1)
			print("checking: ", word1, end=" ")

			for word2 in doc2_actions:
				synset2 = wordnet.synsets(word2)
				sim = []

				for sense1, sense2 in product(synset1, synset2):
					t = wordnet.wup_similarity(sense1, sense2)
					if t != None:
						sim.append(t)

				if sim != []:
					word_sim.append(max(sim))

			if word_sim != []:
				max_word_sim = max(word_sim)
				print(max_word_sim)
				
				if max_word_sim >= ACCEPTED_RATE:
					sentence_sim.append(max_word_sim)
				else:
					sentence_sim.append(None)
			else:
				sentence_sim.append(None)

		# print(sentence_sim)

		match_pair = 0
		for val in sentence_sim:
			if val != None:
				match_pair += 1

		return (match_pair * 100) / len(doc_res1["Action"])
		


if __name__ == "__main__":
	text1 = "The legal system is made up of civil courts, criminal courts and specialty courts, such as family law courts and bankruptcy courts."
	text2 = "The legal system is made up of criminal and civil courts and specialty courts like bankruptcy and family law courts."
	ptext = input("text1: ")
	otext = input("text2: ")
	if len(ptext) == 0 or len(otext) == 0:
		print(sentence_similarity(text1, text2))
	else:
		print(sentence_similarity(ptext, otext))



