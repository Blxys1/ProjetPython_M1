from collections import defaultdict
import re
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix


def tokenize(text):
    # Trouve les mots dans le texte, en utilisant des délimiteurs de mots (espaces, ponctuation...)
    words = re.findall(r'\b\w+\b', text.lower())  # correction du motif regex
    return words


def build_vocab(documents):
    vocab = {}
    word_id = 0
    for doc in documents:
        words = tokenize(doc)
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
        words = tokenize(doc)
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
    mat_TFxIDF = mat_TF.copy().astype(float)
    for word, stats in vocab.items():
        word_id = stats['id']
        doc_count = stats['doc_count']
        if doc_count > 0:
            idf = np.log((num_docs + 1) / (doc_count + 1)) + 1
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
    query_vector = query_vector.reshape(1, -1)
    similarities = cosine_similarity(query_vector, mat_TFxIDF).flatten()
    return similarities


def get_top_results(similarities, documents, top_n=5):
    top_indices = similarities.argsort()[::-1][:top_n]
    top_scores = similarities[top_indices]
    results = pd.DataFrame({
        'Document': [documents[i] for i in top_indices],  # 'titre' remplacé par le texte direct
        'Similarity Score': top_scores
    })
    return results


documents = [
    "Artificial intelligence in healthcare test",
    "Machine learning test applications in finance",
    "Deep learning test advancements",
    "AI for healthcare test and medical diagnosis"
]

vocab = build_vocab(documents)

mat_TF = build_term_frequency_matrix(documents, vocab)
print("Term Frequency Matrix:\n", mat_TF.toarray())

mat_TFxIDF = compute_tfidf_matrix(mat_TF, vocab, len(documents))
print("TF-IDF Matrix:\n", mat_TFxIDF.toarray())

keywords = "test AI healthcare"
query_vector = create_query_vector(keywords, vocab)
print("Query Vector:", query_vector)

similarities = search_documents(query_vector, mat_TFxIDF)
print("Similarities:", similarities)

results = get_top_results(similarities, documents, top_n=3)
print("Top Results:\n", results)
