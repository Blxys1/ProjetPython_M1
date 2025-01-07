
import praw



import urllib.request



import xmltodict



import datetime



from Document import Document  



from Author import Author  



from Corpus import Corpus



from datetime import datetime



from datetime import timezone



import SearchEngine



from document_factory import DocumentFactory



import numpy as np



from scipy.sparse import csr_matrix



from sklearn.metrics.pairwise import cosine_similarity



import pandas as pd



import re



from collections import defaultdict















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











corpus = Corpus.get_instance("Your Corpus Name", collection)











#maybe delete this part



for doc in collection:



    corpus.ajouter_document(doc)



print(corpus)



###







corpus.afficher_documents_par_date(5)



corpus.afficher_documents_par_titre(5)







print("-----------------------------------------------------------------------------------------------------------")



print("~~~~~~~~~~~~~~~~~~Search in the corpus~~~~~~~~~~~~~~~~~~")



keyword=input("Enter a keyword to search in the corpus: ")



matches= corpus.search(keyword)







print(corpus.id2doc.values())







# Use SearchEngine to search for the keyword in the corpus



search_engine =SearchEngine.SearchEngine(list(corpus.id2doc.values()))





search_results = search_engine.search(keyword)







print("Search Results:")



print(search_results)



print("--------------------------------IGNORE THIS PART ---------------------------------------------------------------------------")



print("Matches found in the corpus:", len(matches))



print("-----------------------------------------------------------------------------------------------------------")



concordance_table = corpus.concorde(keyword, context_size=5)



print(concordance_table)



print("----------------------------STOP-------------------------------------------------------------------------------")







# Vocabulary and word frequency



corpus.construire_vocabulaire()  # Build the vocabulary



corpus.compter_frequence_mots()  # Count word frequencies







# Display the vocabulary and word frequencies



print("Vocabulary size:", len(corpus.vocabulaire))



corpus.freq_df = corpus.freq_df.sort_values(by="Frequence", ascending=False)



print("Top 10 most frequent words:")



print(corpus.freq_df.head(10))  # Display top 10 most frequent words











corpus.save('corpus.pkl')



loaded_corpus = Corpus.load('corpus.pkl')



print(loaded_corpus)



corpus.save_to_csv('corpus.csv')