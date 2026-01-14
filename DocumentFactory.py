# DocumentFactory.py
from Document import Document, RedditDocument, ArxivDocument

class DocumentFactory:
    """
    Usine de création de documents
    """

    @staticmethod
    def create_document(doc_type, **kwargs):
        if doc_type == "Reddit":
            return RedditDocument(
                titre=kwargs["titre"],
                auteur=kwargs["auteur"],
                date=kwargs["date"],
                url=kwargs["url"],
                texte=kwargs["texte"],
                nb_comments=kwargs["nb_comments"]
            )

        elif doc_type == "Arxiv":
            return ArxivDocument(
                titre=kwargs["titre"],
                auteurs=kwargs["auteurs"],
                date=kwargs["date"],
                url=kwargs["url"],
                texte=kwargs["texte"]
            )

        else:
            return Document(
                titre=kwargs["titre"],
                auteur=kwargs["auteur"],
                date=kwargs["date"],
                url=kwargs["url"],
                texte=kwargs["texte"]
            )
