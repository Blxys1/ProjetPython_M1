
from Corpus import *

from Document import *

import scipy as sp 

import re

from scipy.sparse import csr_matrix

import numpy as np

from collections import defaultdict

from sklearn.metrics.pairwise import cosine_similarity





class SearchEngine:

    def __init__(self, documents):

        self.documents = documents

        self.vocab = build_vocab(documents)

        self.mat_TF = build_term_frequency_matrix(documents, self.vocab)

        self.mat_TFxIDF = compute_tfidf_matrix(self.mat_TF, self.vocab, len(documents))



    def search(self, keywords, top_n=5):

        query_vector = create_query_vector(keywords, self.vocab)

        similarities = search_documents(query_vector, self.mat_TFxIDF)

        results = get_top_results(similarities, self.documents, top_n)

        return results

    

def tokenize(texte):

    words = re.findall(r'\b\w+\b', texte.lower())  # Convert text to lowercase and split into words

    return words



def build_vocab(documents):

    vocab = {}

    word_id = 0

    for doc in documents:

        if isinstance(doc, Document):  # Vérifie si c'est un objet Document

            texte = doc.texte  # Récupère le texte de l'objet Document

        else:

            texte = str(doc)  # Si ce n'est pas un Document, force une conversion en chaîne



        words = tokenize(texte)  # Passe le texte à tokenize

        for word in words:

            if word not in vocab:

                vocab[word] = {'id': word_id, 'total_occurrences': 0, 'doc_count': 0}

                word_id += 1

    return vocab







def build_term_frequency_matrix(documents, vocab):

    num_docs = len(documents)

    num_terms = len(vocab)

    data, rows, cols = [], [], []



    for doc_id, doc in enumerate(documents):

        if isinstance(doc, Document):  # Vérifie si c'est un objet Document

            texte = doc.texte  # Récupère le texte

        else:

            texte = str(doc)  # Convertit en chaîne si nécessaire



        words = tokenize(texte)  # Passe le texte à tokenize

        word_count = defaultdict(int)

        for word in words:

            word_count[word] += 1



        for word, count in word_count.items():

            if word in vocab:

                word_id = vocab[word]['id']

                data.append(count)

                rows.append(doc_id)

                cols.append(word_id)



                vocab[word]['total_occurrences'] += count

                vocab[word]['doc_count'] += 1



    mat_TF = csr_matrix((data, (rows, cols)), shape=(num_docs, num_terms))

    return mat_TF



    

def compute_tfidf_matrix(mat_TF, vocab, num_docs):

    mat_TFxIDF = mat_TF.copy().astype(float)  # Make a copy and set type to float for correct TF-IDF values

    for word, stats in vocab.items():

        word_id = stats['id']

        doc_count = stats['doc_count']

        if doc_count > 0:

            idf = np.log((num_docs + 1) / (doc_count + 1)) + 1  # Adding 1 to avoid zero issues in log

                

            # Multiply the term frequency for each document by the IDF

            mat_TFxIDF[:, word_id] = mat_TF[:, word_id].multiply(idf)



    return mat_TFxIDF





def create_query_vector(keywords, vocab):

    query_vector = np.zeros(len(vocab))

    

    for word in tokenize(keywords):

        if word in vocab:

            word_id = vocab[word]['id']

            query_vector[word_id] += 1  



    return query_vector





def search_documents(query_vector, mat_TFxIDF):

    # Reshape query vector to be 2D for compatibility

    query_vector = query_vector.reshape(1, -1)

    # Compute cosine similarity between query and document vectors

    similarities = cosine_similarity(query_vector, mat_TFxIDF).flatten()

    return similarities



import pandas as pd



def get_top_results(similarities, documents, top_n=5):

    # Sort scores 

    top_indices = similarities.argsort()[::-1][:top_n]

    top_scores = similarities[top_indices]



    # Create a DataFrame to display the results

    results = pd.DataFrame({

        'Document': [documents[i] for i in top_indices],

        'Similarity Score': top_scores

    })

    return results
