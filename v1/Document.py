from datetime import datetime

class Document:
    def __init__(self, titre, auteur, date, url, texte, type_document='Inconnu'):
        self.titre = titre
        self.auteur = auteur
        self.date = date 
        self.url = url
        self.texte = texte
        self.type_document = type_document

    def afficher_informations(self):
        print(f"Titre: {self.titre}")
        print(f"Auteur: {self.auteur}")
        print(f"Date de publication: {self.date.strftime('%Y-%m-%dT%H:%M:%SZ')}")
        print(f"URL: {self.url}")
        print(f"Texte: {self.texte}")
    
    def __str__(self):
        return self.titre
    
    def getType(self):
        return self.type_document

# Ajoutez cette partie à votre fichier Document.py
class RedditDocument(Document):
    def __init__(self, titre, auteur, date, url, texte, score, nb_commentaires):
        super().__init__(titre, auteur, date, url, texte, 'Reddit')
        self.score = score
        self.nb_commentaires = nb_commentaires

    def __str__(self):
        return f"{super().__str__()} - Score: {self.score}, Commentaires: {self.nb_commentaires}"

    def afficher_informations(self):
        super().afficher_informations()
        print(f"Score: {self.score}")
        print(f"Nombre de commentaires: {self.nb_commentaires}")

class ArxivDocument(Document):
    def __init__(self, titre, auteur, date, url, texte, categories, co_auteurs):
        super().__init__(titre, auteur, date, url, texte, 'Arxiv')
        self.categories = categories
        self.co_auteurs = co_auteurs

    def __str__(self):
        return f"{super().__str__()} - Categories: {', '.join(self.categories)}, Co-auteurs: {self.co_auteurs}"

    def afficher_informations(self):
        super().afficher_informations()
        print(f"Categories: {', '.join(self.categories)}")
        print(f"Co-auteurs: {', '.join(self.co_auteurs)}")
