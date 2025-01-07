class Author:
    def __init__(self, name):
        self.name = name
        self.ndoc = 0
        self.production = {}
  
    def add(self, doc_id, doc):
        self.production[doc_id] = doc
        self.ndoc += 1  # Increment the number of documents

    # Method to display a summary of the author
    def __str__(self):
        return f"Author: {self.name}, Documents published: {self.ndoc}"
