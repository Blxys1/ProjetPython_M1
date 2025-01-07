
from Document import RedditDocument
from Document import ArxivDocument


class DocumentFactory:
    @staticmethod
    def create_document(source, **kwargs):
        if source == "Reddit":
            return RedditDocument(**kwargs)
        elif source == "Arxiv":
            return ArxivDocument(**kwargs)
        else:
            raise ValueError("Source inconnue pour la création du document")
