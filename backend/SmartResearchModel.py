import os 
import pdftotext
from docx import Document 
import glob 
from tqdm import tqdm
import re 
import numpy as np
from haystack.nodes import PreProcessor, AnswerParser, PromptNode, PromptModel, PromptTemplate
from cleanText import clean_text_both


#bdd en mémoire
from haystack.document_stores import InMemoryDocumentStore

#bdd weaviate
from haystack.document_stores import WeaviateDocumentStore
import time
import logging
from pathlib import Path
from typing import Union, Tuple
import subprocess
import requests
import getpass
import weaviate
from weaviate.util import generate_uuid5
import json

#modèles
import torch 
from haystack.nodes import EmbeddingRetriever
from haystack.nodes import BM25Retriever
from haystack.nodes.retriever.dense import DensePassageRetriever
from haystack.nodes import FARMReader

#classifieur
import spacy
from haystack import BaseComponent
from typing import List
from nodeClassification import CustomQueryClassifier

#réseau architecture
from haystack import Pipeline, Answer
from haystack.utils import print_answers
from haystack.utils import launch_weaviate

#Oders pages
import FilesDataExtraction
from typing import List
from haystack import Document, Answer

# #chargement des dataset
# import json 

# #évaluation
# import numpy as np 
# import string
# from transformers import AutoTokenizer, AutoModel
# from sentence_transformers import SentenceTransformer, util
# from IPython.utils import capture


repertoire_fichiers_a_traiter = "Path_of_folder_that_contains_documents_from_which_search_terms_will_be_based_on"
openai_api_key = "Your_openai_key"
deployment_name = "Your_openai_Project_name"
base_url = "Your_openai_server_url"


## Global config 

# Choisir la bdd (memory efficace pour tester du code mais supporte peu de data)
# Choisir si l'on veut charger les data et modèle ou si l'on veut les re écrire dans la bdd
BDD_CHOICE = "memory"   # weaviate ou memory
#LOAD_DATA = True #Si on veut charger les données (pas obligatoire si on charge la bdd sans vouloir la re-créer)
CREATE_BDD = True # True effectue le preprocessing l'écriture l'embeding et le stockage des data dans la bdd
INDEX = "Siamois" #dans weaviate on choisit la bdd que l'on veut (modèle DPR ou Siamois)

## Modèle config

model_retriever_siamois = "dangvantuan/sentence-camembert-base"  #Autre modèle siamois : dangvantuan/CrossEncoder-camembert-large

model_retriever_dpr_ctx = "etalab-ia/dpr-question_encoder-fr_qa-camembert"
model_retriever_dpr_query = "etalab-ia/dpr-ctx_encoder-fr_qa-camembert"

model_reader = "CATIE-AQ/QAmembert"  #Autre modèle utilisé : etalab-ia/camembert-base-squadFR-fquad-piaf
context_window_size = 500

def init_smart_research(LOAD_DATA):
    # A
    # Le preprocesseur est initialisé et utilisé pour normaliser les espaces blancs, supprimer les en-tete et pied de page puis les lignes vides
    # Ce fractionnement du document est réalisé pour les documents longs afin de faciliter le travail du retriever
    # Préparation des fichiers à la recherche
    preprocessor = PreProcessor(
        clean_empty_lines=False,
        clean_whitespace=True,
        clean_header_footer=True,
        split_by="passage",
        split_length=1,
        split_respect_sentence_boundary=False,
        #split_overlap=5,
        add_page_number=True,
        language="fr",
        id_hash_keys=["content"]
    )
    #Alternative lorsque le update embedding ne marche pas
    def pre_embedder(docs):
        print('Running the pre-embedding with siamois model')
        retriever_dense_siamois = EmbeddingRetriever(
                                                    document_store=document_store,
                                                    embedding_model=model_retriever_siamois,
                                                    use_gpu=True
                                                    )
        embeds = retriever_dense_siamois.embed_documents(docs)
        for doc, emb in zip(docs,embeds):
            doc.embedding = emb
        return docs

    if LOAD_DATA :
        #B
        # GET All documents refactoring content As dictiannary
        data_list_of_dict=FilesDataExtraction.extractFiles_process(repertoire_fichiers_a_traiter)
        
        #cut in a set of paragraph for all documents 
        docs_process = preprocessor.process(data_list_of_dict)

        if CREATE_BDD :

            if BDD_CHOICE == "weaviate" :

                    #Créer une instance WCS (Weaviate Cluster Service)
                client = weaviate.Client(url="https://my-test-cluster-piumer61.weaviate.network", auth_client_secret=weaviate.AuthApiKey(api_key="BKdXvQEPwLMFV3nsRRKhYz0PUVqXoDKNRlMg"),)
                
                client.batch.configure(
                        batch_size=100,
                        # dynamically update the `batch_size` based on import speed
                        dynamic=False,
                        # `timeout_retries` takes an `int` value to retry on time outs
                        timeout_retries=3,
                        # checks for batch-item creation errors
                        # this is the default in weaviate-client >= 3.6.0
                        callback=weaviate.util.check_batch_result,
                        consistency_level=weaviate.data.replication.ConsistencyLevel.ALL)
                #client.batch.add_data_object(docs_process, "Paragraph")

                #Connexion à weaviate 
                document_store = WeaviateDocumentStore(host="https://my-test-cluster-piumer61.weaviate.network", index=INDEX, recreate_index=CREATE_BDD, similarity="dot_product",
                                                                        progress_bar=True, duplicate_documents="overwrite") # Weaviate fonctionne sur http://localhost:8080

                #embedding des docs via modèle siamois 
                docs_process = pre_embedder(docs_process)
                        #Ecriture des documents et de leur embeding dans la bdd
                document_store.write_documents(documents=docs_process, index=INDEX, batch_size=100,
                                                                duplicate_documents="overwrite")
            elif BDD_CHOICE == "memory" : 
                document_store = InMemoryDocumentStore(use_bm25=True) #Connexion bdd en mémoire
                document_store.delete_documents() #suppression des documents qui pourrait rester
                document_store.write_documents(docs_process)  #écriture des documents
                print(f"nombre de document chargés : {document_store.get_document_count()}")
        
    else :    
        document_store = WeaviateDocumentStore(index=INDEX,recreate_index=CREATE_BDD, similarity="dot_product",
                                                                progress_bar=True, duplicate_documents="overwrite") # Weaviate fonctionne sur http://localhost:8080
        print(f"index chargé : {document_store.index}, nombre d'embedding : {document_store.get_embedding_count()}, nombre de document chargés : {document_store.get_document_count()}")

        #instanciation des deux autres modèles d'encodage type sparse avec BM25        
    retriever_BM25_req = BM25Retriever(document_store)
    retriever_BM25_comp = BM25Retriever(document_store)
        #retriever_BM25forDense = BM25Retriever(document_store)
        
        #instanciation du modèle reader de question réponse extraite        
    reader = FARMReader(
                    model_name_or_path=model_reader,
                    use_gpu=True, no_ans_boost=-10, context_window_size=context_window_size,
                    top_k_per_candidate=10, top_k_per_sample=5,
                    num_processes=8, max_seq_len=400)
    
    #modèle GPT
    prompt_small_V2 = """Tu es un expert en linguistique et tu sais faire de manière précise la reformulation de réponse a une question sur tous types de sujets. Reformule cette réponse l'améliorant d'un point de vue syntaxique car ce sont des élements de réponses qui ont été mis bout à bout tout en gardant les notions et arguments importants :
    {join(documents, delimiter=new_line)}.
    Cette réponse provient de la question suivante :\n{query}"""
        
        #instanciation du classifieur
    smart_answer_prompt = PromptTemplate(
    prompt=prompt_small_V2,
    output_parser=AnswerParser())

    #instancaition modele GPT
    azure_chat = PromptModel(
    model_name_or_path="gpt-35-turbo",
    api_key=openai_api_key,
    model_kwargs={
        "azure_deployment_name": deployment_name,
        "azure_base_url": base_url,
        "api_version":"2023-03-15-preview",
        "temperature":1, 
        "top_k":1,
        "max_tokens":1536
    },
    )

    prompt_node = PromptNode(model_name_or_path=azure_chat, default_prompt_template=smart_answer_prompt)

        #noeud qui concatène la listes des réponses en une seule réponse pour GPT 
    class join_answers(BaseComponent):
        outgoing_edges = 1
        def run(self, query: str, answers: List[Answer]):
            answers_list = []
            for ans_obj in answers:
                answers_list.append(ans_obj.answer)
            answers_join = ', '.join(answers_list)
            output={
                "documents": [Document(answers_join)]
            }
            return output, "output_1"
    #     def run_batch(self, queries: list):
    #         return [self.run(query, docs) for query, docs in zip(queries, answers)]
        def run_batch(self, queries: List[str],answers: List[Answer]):
            pass


        #instanciation de la pipeline
        #juste ret sparse BM-25
    p = Pipeline()
    p.add_node(component=CustomQueryClassifier(), name="QueryClassifier", inputs=["Query"])
    p.add_node(component=retriever_BM25_req, name="RetrieverBM25-REQ", inputs=["QueryClassifier.output_1"])
    p.add_node(component=retriever_BM25_comp, name="RetrieverBM25-COMP", inputs=["QueryClassifier.output_2"])
    p.add_node(component=reader, name="QAReader", inputs=["RetrieverBM25-COMP"])
    p.add_node(component=join_answers(), name="JoinAnswers", inputs=["QAReader"])
    p.add_node(component=prompt_node, name="GPTanswer", inputs=["JoinAnswers.output_1"])
    print(f"Pipeline instancier avec succès contenant les composants : {p.components}")
    #Utilisation de la pipeline a partir d'une requète d'un utilisateur 
    return p


def process_query(query,p):
    answers = p.run(query=clean_text_both(query),  params={
                                            "RetrieverBM25-COMP": {"top_k": 5, "debug": True}, #param k 
                                            "RetrieverBM25-REQ": {"top_k": 3, "debug": True}, #param k 
                                        #    "RetrieverBM25forsiamois": {"top_k": 25, "debug": True},
    #                                         "RetrieverDPR": {"top_k": 5, "debug": True}, #param k
                                            "QAReader": {"top_k": 3, "debug": True}, #param s
                                            "GPTanswer": {"debug": True}
                                        })
    return answers    
   