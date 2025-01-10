import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
from Main import (  # Importez toutes les fonctions nécessaires
    ajouter_document,
    scrape_newsapi,
    scrape_arxiv,
    process_documents,
    save_corpus_to_file,
    load_corpus_from_file,
    id2doc,
    id2aut,
    current_id,
    corpus
)

def test_ajouter_document():
    # Réinitialiser les variables globales
    global id2doc, current_id
    id2doc.clear()
    current_id = 1

    # Données de test
    titre = "Titre Exemple"
    auteur = "Auteur Exemple"
    date_str = "2023-01-01"
    url = "http://example.com"
    texte = "Contenu de test"
    
    # Appel de la fonction
    ajouter_document(titre, auteur, date_str, url, texte)
    
    # Assertions
    assert len(id2doc) == 1  # Vérifie qu'un document a été ajouté
    doc = id2doc[1]
    assert doc.titre == titre  # Vérifie le titre
    assert doc.auteur == auteur  # Vérifie l'auteur
    assert doc.date == datetime.strptime(date_str, '%Y-%m-%d')  # Vérifie la date
    assert doc.url == url  # Vérifie l'URL
    assert doc.texte == texte  # Vérifie le texte

# Test pour `scrape_newsapi`
@patch("Main.NewsApiClient")
def test_scrape_newsapi(mock_newsapi_client):
    mock_instance = mock_newsapi_client.return_value
    mock_instance.get_everything.return_value = {
        "articles": [
            {"title": "Article 1", "description": "Description 1", "author": "Author 1", "publishedAt": "2023-01-01T00:00:00Z", "url": "http://example.com/1"},
            {"title": "Article 2", "description": "Description 2", "author": "Author 2", "publishedAt": "2023-01-02T00:00:00Z", "url": "http://example.com/2"},
        ]
    }
    result = scrape_newsapi("test")
    assert len(result) == 2
    assert result[0][0] == "NewsAPI"
    assert result[1][1]["title"] == "Article 2"

# Test pour `scrape_arxiv`
@patch("Main.urllib.request.urlopen")
@patch("Main.xmltodict.parse")
def test_scrape_arxiv(mock_xmltodict_parse, mock_urlopen):
    mock_urlopen.return_value.read.return_value.decode.return_value = "<feed><entry><title>ArXiv Paper</title></entry></feed>"
    mock_xmltodict_parse.return_value = {
        "feed": {
            "entry": [{"title": "ArXiv Paper", "summary": "This is a summary", "author": [{"name": "Author A"}], "published": "2023-01-01T00:00:00Z"}]
        }
    }
    result = scrape_arxiv("test")
    assert len(result) == 1
    assert result[0][0] == "Arxiv"
    assert "ArXiv Paper" in result[0][1]["title"]

# Test pour `process_documents`
@patch("Main.Corpus.get_instance")
def process_documents(docs_bruts):
    global current_id, id2aut, corpus
    collection = []

    for source, doc in docs_bruts:
        if source == 'Arxiv':
            titre = doc['title'].replace('\n', " ")
            texte = doc['summary'].replace('\n', " ")
            authors = ", ".join([a['name'] for a in doc['author']]) if isinstance(doc['author'], list) else doc['author']['name']
            date = datetime.strptime(doc['published'], '%Y-%m-%dT%H:%M:%S%z')
            document = Document(titre, authors, date, doc['id'], texte)
        elif source == 'NewsAPI':
            titre = doc['title'] or 'No Title'
            texte = doc['description'] or 'No Description'
            authors = doc.get('author', 'Unknown Author')
            date = datetime.strptime(doc['publishedAt'], '%Y-%m-%dT%H:%M:%SZ')
            document = Document(titre, authors, date, doc['url'], texte)
        collection.append(document)
        id2doc[current_id] = document
        
        if document.auteur not in id2aut:
            id2aut[document.auteur] = Author(document.auteur)
        id2aut[document.auteur].add(current_id, document)
        current_id += 1
    # Update or initialize corpus
    if corpus is None:
        corpus = Corpus.get_instance("Corpus", collection)
    else:
        for doc in collection:
            corpus.ajouter_document(doc)
    return collection

# Test pour `save_corpus_to_file`
@patch("Main.pickle.dump")
def test_save_corpus_to_file(mock_pickle_dump):
    save_corpus_to_file("test.pkl")
    mock_pickle_dump.assert_called_once()

# Test pour `load_corpus_from_file`
@patch("Main.pickle.load")
@patch("Main.open")
def load_corpus_from_file(filename="scraped_data.pkl"):
    global id2doc, id2aut, corpus  # Déclaration des variables globales
    try:
        with open(filename, "rb") as f:
            id2doc, id2aut, corpus = pickle.load(f)
    except FileNotFoundError:
        print(f"File {filename} not found.")

