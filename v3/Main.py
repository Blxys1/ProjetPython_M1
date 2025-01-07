import urllib.request
import xmltodict
from datetime import datetime
from Document import Document  
from Author import Author  
from Corpus import Corpus
from newsapi import NewsApiClient
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import pickle

# Global Variables
id2doc = {}
id2aut = {}
current_id = 1
corpus = None  # Singleton instance of Corpus
processed_collection = []

# Function to add a document
def ajouter_document(titre, auteur, date_str, url, texte):
    global current_id
    date = datetime.strptime(date_str, '%Y-%m-%d')
    document = Document(titre, auteur, date, url, texte)
    id2doc[current_id] = document
    current_id += 1

# Function to scrape NewsAPI
def scrape_newsapi(keyword):
    api = NewsApiClient(api_key='af8a9cab26f24d22921b4f5e0c323b33') 
    try:
        response = api.get_everything(q=keyword, language='en', page_size=10)
        docs_bruts = [('NewsAPI', article) for article in response['articles']]
    except Exception as e:
        messagebox.showerror("Error", f"NewsAPI Scraping Failed: {e}")
        return []
    return docs_bruts

# Function to scrape ArXiv
def scrape_arxiv(keyword):
    try:
        url = f'http://export.arxiv.org/api/query?search_query=all:{keyword}&start=0&max_results=10'
        url_read = urllib.request.urlopen(url)
        data = url_read.read().decode('utf-8')
        dico = xmltodict.parse(data)
        docs = dico['feed']['entry'] if isinstance(dico['feed']['entry'], list) else [dico['feed']['entry']]
        docs_bruts = [('Arxiv', doc) for doc in docs]
    except Exception as e:
        messagebox.showerror("Error", f"ArXiv Scraping Failed: {e}")
        return []
    return docs_bruts

# Function to process documents
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

# Functions to save and load corpus
def save_corpus_to_file(filename="scraped_data.pkl"):
    with open(filename, "wb") as f:
        pickle.dump((id2doc, id2aut, corpus), f)

def load_corpus_from_file(filename="scraped_data.pkl"):
    global id2doc, id2aut, corpus
    try:
        with open(filename, "rb") as f:
            id2doc, id2aut, corpus = pickle.load(f)
    except FileNotFoundError:
        messagebox.showwarning("Load Error", "No saved data found. Please scrape first!")

# Tkinter Interface
def create_interface():
    def on_scrape():
        keyword = keyword_entry.get()
        if not keyword:
            messagebox.showwarning("Input Error", "Please enter a keyword!")
            return

        # Clear results area
        results_text.delete("1.0", tk.END)
        results_text.insert(tk.END, f"Scraping data for keyword: {keyword}\n")

        def scrape_and_process():
            try:
                # Scrape data from sources
                docs_bruts = scrape_newsapi(keyword) + scrape_arxiv(keyword)

                global processed_collection

                # Process documents and save to file
                processed_collection = process_documents(docs_bruts)
                save_corpus_to_file()

                # Get the singleton instance of the Corpus class
                corpus = Corpus.get_instance()

                # Clear the corpus and load new documents
                corpus.vider()  # Ensure the corpus is emptied before adding new docs
                for doc in processed_collection:
                    corpus.ajouter_document(doc)

                # Update UI with results
                results_text.insert(tk.END, "Scraping completed and data saved!\n")
                for doc in processed_collection:
                    results_text.insert(tk.END, f"- Title: {doc.titre}\n  Author(s): {doc.auteur}\n\n")
            except Exception as e:
                results_text.insert(tk.END, f"Error during scraping: {e}\n")

        threading.Thread(target=scrape_and_process).start()

    def on_search():
        keyword = keyword_entry.get()
        if not keyword:
            messagebox.showwarning("Input Error", "Please enter a keyword!")
            return

        # Load the corpus if not already loaded
        if corpus is None:
            load_corpus_from_file()

        results_text.delete("1.0", tk.END)
        results_text.insert(tk.END, f"Searching for '{keyword}' in the corpus...\n")
        
        try:
            search_results = corpus.search(keyword)
            if search_results:
                for doc in search_results:
                    results_text.insert(tk.END, f"- Title: {doc.titre}\n  Author(s): {doc.auteur}\n\n")
            else:
                results_text.insert(tk.END, "No documents found.\n")
        except Exception as e:
            results_text.insert(tk.END, f"Error during search: {e}\n")

    def on_corpus_stats():
        if corpus is None:
            load_corpus_from_file()

        results_text.delete("1.0", tk.END)
        results_text.insert(tk.END, "Calculating corpus statistics...\n")
        
        try:
            corpus.construire_vocabulaire()
            corpus.compter_frequence_mots()

            results_text.insert(tk.END, f"Vocabulary size: {len(corpus.vocabulaire)}\n")
            corpus.freq_df = corpus.freq_df.sort_values(by="Frequence", ascending=False)

            results_text.insert(tk.END, "Top 10 most frequent words:\n")
            results_text.insert(tk.END, corpus.freq_df.head(10).to_string() + "\n")
        except Exception as e:
            results_text.insert(tk.END, f"Error calculating corpus statistics: {e}\n")

    def on_author_stats():
        if corpus is None:
            load_corpus_from_file()

        author_name = simpledialog.askstring("Author Statistics", "Enter the author's name:")
        if not author_name:
            return

        results_text.delete("1.0", tk.END)
        try:
            if author_name in id2aut:
                author = id2aut[author_name]
                total_length = sum(len(doc.texte) for doc in author.production.values())
                avg_length = total_length / author.ndoc if author.ndoc > 0 else 0

                results_text.insert(tk.END, f"Author: {author.name}\n")
                results_text.insert(tk.END, f"Number of documents: {author.ndoc}\n")
                results_text.insert(tk.END, f"Average document length: {avg_length:.2f} characters\n")
            else:
                results_text.insert(tk.END, f"Author {author_name} not found.\n")
        except Exception as e:
            results_text.insert(tk.END, f"Error during author stats: {e}\n")

    # Main Tkinter Window
    window = tk.Tk()
    window.title("Enhanced Search Engine Interface")
    window.geometry("900x600")

    # Keyword Input
    tk.Label(window, text="Enter Keyword:", font=("Arial", 12)).pack(pady=5)
    keyword_entry = tk.Entry(window, font=("Arial", 12), width=50)
    keyword_entry.pack(pady=5)

    # Buttons
    button_frame = tk.Frame(window)
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="Scrape Data", font=("Arial", 12), command=on_scrape).pack(side=tk.LEFT, padx=10)
    tk.Button(button_frame, text="Search", font=("Arial", 12), command=on_search).pack(side=tk.LEFT, padx=10)
    tk.Button(button_frame, text="Corpus Stats", font=("Arial", 12), command=on_corpus_stats).pack(side=tk.LEFT, padx=10)
    tk.Button(button_frame, text="Author Stats", font=("Arial", 12), command=on_author_stats).pack(side=tk.LEFT, padx=10)

    # Results Area
    results_frame = tk.Frame(window)
    results_frame.pack(fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(results_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    results_text = tk.Text(results_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set, font=("Arial", 12))
    results_text.pack(fill=tk.BOTH, expand=True)

    scrollbar.config(command=results_text.yview)
    window.mainloop()

if __name__ == "__main__":
    create_interface()
