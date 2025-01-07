import pickle
import pandas as pd
import Author
from datetime import timezone


class Corpus:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Corpus, cls).__new__(cls)
            return cls._instance
        else:
            raise Exception("Corpus is a singleton class. Use Corpus.get_instance() to get the instance.")
    def __init__(self, nom):
        if not hasattr(self, 'initialized'):
            self.nom = nom
            self.authors = {} 
            self.id2doc = {} 
            self.ndoc = 1 
            self.naut = 0 
            self.initialized = True
    @classmethod
    def get_instance(cls, nom='default_name'):
        if cls._instance is None:
            cls._instance = Corpus(nom)  # Initializes the singleton instance
        return cls._instance
        
    def __reduce__(self):
        return (self.get_instance, (self.nom,))

    # Method to add documents
    def ajouter_document(self, document):
        self.id2doc[self.ndoc] = document
        self.ndoc += 1
        
        # Ensure the author exists in the author dictionary
        if document.auteur not in self.authors:
            self.authors[document.auteur] = Author.Author(document.auteur)
            self.naut += 1
        
        # Add document to author's production
        self.authors[document.auteur].add(self.ndoc, document)

    # Method to sort and display documents by date
    """
    def afficher_documents_par_date(self, n):
        sorted_docs = sorted(self.id2doc.values(), key=lambda doc: doc.date)
        for doc in sorted_docs[:n]:
            doc.afficher_informations() """
    def afficher_documents_par_date(self, n):
        # Ensure all dates are aware
        for doc in self.id2doc.values():
            if doc.date.tzinfo is None:  # If the date is naive
                doc.date = doc.date.replace(tzinfo=timezone.utc)  # or specify a different timezone

        # Sort and display
        sorted_docs = sorted(self.id2doc.values(), key=lambda doc: doc.date)
        for doc in sorted_docs[:n]:
            doc.afficher_informations()

    # Method to sort and display documents by title
    def afficher_documents_par_titre(self, n):
        sorted_docs = sorted(self.id2doc.values(), key=lambda doc: doc.titre)
        for doc in sorted_docs[:n]:
            doc.afficher_informations()

    # Representation method
    def __repr__(self):
        return f"Corpus: {self.nom}, Documents: {self.ndoc}, Authors: {self.naut}"

    # Method to save the corpus to disk (using pickle)
    def save(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self, f)
        print(f"Corpus saved to {filename}")

    # Method to load the corpus from disk
    @classmethod
    def load(cls, filename):
        with open(filename, 'rb') as f:
            cls._instance = pickle.load(f)
        return cls._instance

    # Optional method to save to CSV using DataFrame
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
