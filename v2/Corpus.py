import pickle

import pandas as pd

import re

from datetime import timezone

from collections import defaultdict

from Author import Author

from SearchEngine  import *

from SearchEngine import build_vocab, build_term_frequency_matrix

from SearchEngine import compute_tfidf_matrix
from SearchEngine import create_query_vector



class Corpus:

    _instance = None

    _concatenated_text = None



    def __new__(cls, *args, **kwargs):

        if cls._instance is None:

            cls._instance = super(Corpus, cls).__new__(cls)

            return cls._instance

        else:

            raise Exception("Corpus is a singleton class. Use Corpus.get_instance() to get the instance.")

    

    def __init__(self, nom, documents=None):

        if not hasattr(self, 'initialized'):

            self.nom = nom

            self.authors = {} 

            self.id2doc = {} 

            self.ndoc = 1 

            self.naut = 0 

            self.initialized = True

            # Initialize the corpus with the provided documents

            if documents:

                self.vocab = build_vocab([doc.texte for doc in documents])  # Pass only the text content of each document

                self.mat_TF = build_term_frequency_matrix([doc.texte for doc in documents], self.vocab)  # Pass doc.texte

                self.mat_TFxIDF = compute_tfidf_matrix(self.mat_TF, self.vocab, len(documents))

            else:

                self.vocab = {}

                self.mat_TF = None

                self.mat_TFxIDF = None



    @classmethod

    def get_instance(cls, nom='default_name',documents=None):

        if cls._instance is None:

            cls._instance = Corpus(nom, documents )  # Initializes the singleton instance

        return cls._instance

        

    def __reduce__(self):

        return (self.get_instance, (self.nom,))

    

    def ajouter_document(self, document):

        self.id2doc[self.ndoc] = document

        self.ndoc += 1



        if document.auteur not in self.authors:

            self.authors[document.auteur] = Author(document.auteur)

            self.naut += 1

        

        self.authors[document.auteur].add(self.ndoc, document)

        self.update_vocabulary_and_matrices()



    def update_vocabulary_and_matrices(self):

        """ Rebuilds the vocabulary and term-document matrices after adding a document. """

        self.vocab = build_vocab(list(self.id2doc.values()))  # Rebuild vocabulary

        self.mat_TF = build_term_frequency_matrix(list(self.id2doc.values()), self.vocab)  # Rebuild TF matrix

        self.mat_TFxIDF = compute_tfidf_matrix(self.mat_TF, self.vocab, self.ndoc)  # Rebuild TF-IDF matrix





    def afficher_documents_par_date(self, n):

        for doc in self.id2doc.values():

            if doc.date.tzinfo is None:

                doc.date = doc.date.replace(tzinfo=timezone.utc)



        sorted_docs = sorted(self.id2doc.values(), key=lambda doc: doc.date)

        for doc in sorted_docs[:n]:

            doc.afficher_informations()



    def afficher_documents_par_titre(self, n):

        sorted_docs = sorted(self.id2doc.values(), key=lambda doc: doc.titre)

        for doc in sorted_docs[:n]:

            doc.afficher_informations()



    def __repr__(self):

        return f"Corpus: {self.nom}, Documents: {self.ndoc}, Authors: {self.naut}"



    def save(self, filename):

        with open(filename, 'wb') as f:

            pickle.dump(self, f)

        print(f"Corpus saved to {filename}")



    @classmethod

    def load(cls, filename):

        with open(filename, 'rb') as f:

            cls._instance = pickle.load(f)

        return cls._instance



    def save_to_csv(self, filename):

        data = {

            "Title": [doc.titre for doc in self.id2doc.values()],

            "Author": [doc.auteur for doc in self.id2doc.values()],

            "Date": [doc.date.strftime('%Y-%m-%d') for doc in self.id2doc.values()],

            "Text": [doc.texte for doc in self.id2doc.values()],

            "URL": [doc.url for doc in self.id2doc.values()]

        }

        df = pd.DataFrame(data)

        df.to_csv(filename, index=False)

        print(f"Corpus saved to CSV at {filename}")



    def search(self, keyword):

        if Corpus._concatenated_text is None:

            Corpus._concatenated_text = ' '.join(doc.texte for doc in self.id2doc.values())

        

        pattern = re.compile(rf'\b{re.escape(keyword)}\b', re.IGNORECASE)

        matches = pattern.findall(Corpus._concatenated_text)

        return matches



    def concorde(self, expression, context_size=5):

        if Corpus._concatenated_text is None:

            Corpus._concatenated_text = ' '.join(doc.texte for doc in self.id2doc.values())

        

        pattern = re.compile(

            rf'(\S+(?:\s+\S+){{0,{context_size}}})\s+({re.escape(expression)})\s+((?:\S+\s+){{0,{context_size}}}\S+)', 

            re.IGNORECASE

        )

        matches = pattern.findall(Corpus._concatenated_text)

        df = pd.DataFrame(matches, columns=["Contexte Gauche", "Motif Trouvé", "Contexte Droit"])

        return df



    def nettoyer_texte(self, texte):

        texte = texte.lower()

        texte = re.sub(r'\n', ' ', texte)

        texte = re.sub(r'[^\w\s]', ' ', texte)  # Keep words and spaces

        texte = re.sub(r'\d+', '', texte)

        return texte



    def construire_vocabulaire(self):

        vocabulaire = set()

        for doc in self.id2doc.values():

            cleaned_text = self.nettoyer_texte(doc.texte)

            words = cleaned_text.split()

            vocabulaire.update(words)

        

        self.vocabulaire = {word: 0 for word in vocabulaire}



    def compter_frequence_mots(self):

        word_counts = defaultdict(int)

        

        for doc in self.id2doc.values():

            cleaned_text = self.nettoyer_texte(doc.texte)

            words = cleaned_text.split()

            

            for word in words:

                word_counts[word] += 1



        self.freq_df = pd.DataFrame(

            list(word_counts.items()), columns=["Mot", "Frequence"]

        ).sort_values(by="Frequence", ascending=False)



    def SearchEngine(self, keywords, top_n=5):

        query_vector = create_query_vector(keywords, self.vocab)

        similarities = search_documents(query_vector, self.mat_TFxIDF)

        results = get_top_results(similarities, self.documents, top_n)

        return results