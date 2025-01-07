import praw
import urllib.request
import xmltodict
import datetime
from Document import Document  
from Author import Author  
from Corpus import Corpus
from datetime import datetime
from datetime import timezone
from document_factory import DocumentFactory


id2doc = {}
id2aut = {}
current_id = 1  

def ajouter_document(titre, auteur, date_str, url, texte):
    global current_id
    date = datetime.strptime(date_str, '%Y-%m-%d')
    document = Document(titre, auteur, date, url, texte)
    id2doc[current_id] = document
    current_id += 1

# Reddit scraping
key_word = input("Enter a key word \n")
reddit = praw.Reddit(client_id='RYN1CyG93DB6dQ4euoW4Kw',
                     client_secret='L4VN3NPDbIo-lMvx6_z9t0U9HzERpw',
                     user_agent='scrapping exp')
docs_bruts = []
for post in reddit.subreddit(key_word).hot(limit=10):
    docs_bruts.append(('Reddit', post))

# Arxiv API scraping
url = f'http://export.arxiv.org/api/query?search_query=all:{key_word}&start=0&max_results=10'
url_read = urllib.request.urlopen(url)
data = url_read.read().decode('utf-8')
dico = xmltodict.parse(data)
docs = dico['feed']['entry']

for d in docs: 
    docs_bruts.append(('Arxiv', d))

# Process documents from reddit and arxiv
collection = []
for source, doc in docs_bruts:
    if source == 'Arxiv':
        titre = doc['title'].replace('\n', " ")
        texte = doc['summary'].replace('\n', " ")
        try: 
            authors = ", ".join([a['name'] for a in doc['author']])
        except:
            authors = doc['author']['name']
        date = datetime.strptime(doc['published'], '%Y-%m-%dT%H:%M:%S%z')
        document = Document(titre, authors, date, doc['id'], texte)
        collection.append(document)
    
    elif source == 'Reddit':
        titre = doc.title
        texte = doc.selftext
        authors = doc.author
        date = datetime.utcfromtimestamp(doc.created_utc)
        document = Document(titre, authors, date, doc.url, texte)
        collection.append(document)
        
print("Collection of documents:")
for doc in collection:
    doc.afficher_informations()
    print("---")

for doc in collection:
    id2doc[current_id] = doc
    
    if doc.auteur not in id2aut:
        id2aut[doc.auteur] = Author(doc.auteur)
    
    id2aut[doc.auteur].add(current_id, doc)
    current_id += 1

print("Authors and their documents:")
for author in id2aut.values():
    print(f"Author: {author.name}")
    for doc_id, doc in author.production.items():
        print(f"Document ID: {doc_id}, Title: {doc.titre}")
    print("-------Next author-------")

print("-----------------------------------------------------------------------------------------------------------")
print ("Statistics")
def author_statistics(author_name):
    if author_name in id2aut:
        author = id2aut[author_name]
        total_length = sum(len(doc.texte) for doc in author.production.values())
        avg_length = total_length / author.ndoc if author.ndoc > 0 else 0
        print(f"Auteur: {author.name}")
        print(f"Nombre de documents produits: {author.ndoc}")
        print(f"Taille moyenne des documents: {avg_length:.2f} caractères")
    else:
        print(f"Auteur {author_name} non trouvé.")

author_name = input("Entrez le nom de l'auteur pour obtenir des statistiques : ")
author_statistics(author_name)


corpus = Corpus.get_instance()

for doc in collection:
    corpus.ajouter_document(doc)
print(corpus)

corpus.afficher_documents_par_date(5)
corpus.afficher_documents_par_titre(5)

corpus.save('corpus.pkl')
loaded_corpus = Corpus.load('corpus.pkl')
print(loaded_corpus)
corpus.save_to_csv('corpus.csv')