import spacy
import fr_core_news_md
from haystack import BaseComponent

from typing import List
 

#nlp = spacy.load("fr_core_news_md")
nlp = fr_core_news_md.load()
adjectives = []

 
for word in nlp.Defaults.stop_words:
    if nlp.vocab[word].is_stop == True and nlp.vocab[word].is_alpha == True:
        if word.endswith(('quel', 'quelle', 'quels', 'quelles')):
            adjectives.append(word)

#Augmentation de la liste pour la détection de question

 

adjectifs_interrogatifs_sup = ['que', 'quel', 'quelle', 'quels', 'quelles', 'combien', 'quelle(s)', 'quel(s)', 'quels', 'quelles', 'quels', 'quelles', 'lequel', 'laquelle', 'lesquels', 'lesquelles', 'quelque', 'quels', 'quelles']
pronoms_interrogatifs = ["qui","que","quoi","quand","où","comment","combien","pourquoi","lequel","laquelle","lesquels","lesquelles","duquel","de laquelle","desquels","desquelles" ]

 
#liste de détection de mots qui se trouve dans un e question de compréhnsion 
Question_detection = ['?'] + adjectifs_interrogatifs_sup + pronoms_interrogatifs

#On ajoute certains adjectifs qui ne sont pas deja présent 
for adj in adjectives :
    if adj not in Question_detection : Question_detection.append(adj)



#verification de présence d'inversion verne sujet 
def check_verbe_inter_V2(query):

    l_lim_spacy = ["affaiblissons","puis"]

    query = query.lower()

    if "est-elle" in query: #termes mal labelisé comme verbe et pron par spacy check a la main

        return True

    doc = nlp(query)

    n_words = len(doc)

    for i in range(n_words):

        tok = doc[i]

        if i < n_words - 2: 

            tok_next = doc[i+1]

            tok_next_next = doc[i+2]

           # print(tok,tok.pos_, tok_next.text,tok_next.pos_, tok_next_next,tok_next_next.pos_)

            if ((tok.pos_=="VERB" or tok.pos_=="AUX" or tok.text in l_lim_spacy) and tok_next.pos_=="PRON") or ((tok.pos_=="VERB" or tok.pos_=="AUX" or tok.text in l_lim_spacy) and tok_next.text=="-" and tok_next_next.pos_=="PRON") or ((tok_next.pos_=="VERB" or tok_next.text in l_lim_spacy) and tok_next_next.pos_=="PRON"):

                return True


    return False

#fonction qui renvoie true si c'est une question de compréhension 
def check_query_comp(query):

    req_bool=False

    if any(x.lower() in query_word.lower() for x in Question_detection for query_word in query.split()) or check_verbe_inter_V2(query):

       # print("This is a question!",query)

        req_bool = True

    else:

      #  print("This is not a question!",query)

        req_bool = False

    return req_bool
 

 
#noeud de classification
class CustomQueryClassifier(BaseComponent):

    outgoing_edges = 2

 

    def run(self, query: str):

        if check_query_comp(query):

            return {"query":query}, "output_2"

        else:

            return {"query":query}, "output_1"

 

    def run_batch(self, queries: List[str]):

        split = {"output_1": {"queries": []}, "output_2": {"queries": []}}

        for query in queries:

            if  check_query_comp(query):

                split["output_2"]["queries"].append(query)

            else:

                split["output_1"]["queries"].append(query)

 

        return split, "split"