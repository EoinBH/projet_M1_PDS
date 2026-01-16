# DocumentFactory.py

from Document import Document, RedditDocument, ArxivDocument


class DocumentFactory :
    """
    Usine de création de documents à partir de différentes sources
    """

    # Crée et retourne un document en fonction de son type et de ses paramètres
    @staticmethod
    def creer_document(type_document, **parametres) :
        if type_document == "Reddit" :
            return RedditDocument(
                titre=parametres["titre"],
                auteur=parametres["auteur"],
                date=parametres["date"],
                url=parametres["url"],
                texte=parametres["texte"],
                nombre_commentaires=parametres["nombre_commentaires"]
            )

        elif type_document == "Arxiv" :
            return ArxivDocument(
                titre=parametres["titre"],
                auteurs=parametres["auteurs"],
                date=parametres["date"],
                url=parametres["url"],
                texte=parametres["texte"]
            )

        else :
            return Document(
                titre=parametres["titre"],
                auteur=parametres["auteur"],
                date=parametres["date"],
                url=parametres["url"],
                texte=parametres["texte"]
            )
