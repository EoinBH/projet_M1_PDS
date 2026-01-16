# Document.py

from datetime import datetime


class Document :
    """
    Classe mère représentant un document générique
    """

    # Initialise un document générique avec ses métadonnées principales
    def __init__(self, titre, auteur, date, url, texte) :
        self.titre = titre
        self.auteur = auteur
        self.date = datetime.fromtimestamp(date) if date != 0 else None
        self.url = url
        self.texte = texte
        self.type_document = "Document"

    # Retourne le titre du document
    def get_titre(self) :
        return self.titre

    # Retourne l'auteur principal du document
    def get_auteur(self) :
        return self.auteur

    # Retourne la date du document
    def get_date(self) :
        return self.date

    # Retourne l'URL du document
    def get_url(self) :
        return self.url

    # Retourne le texte du document
    def get_texte(self) :
        return self.texte

    # Retourne le type du document
    def get_type(self) :
        return self.type_document

    # Retourne une représentation textuelle du document
    def __str__(self) :
        return self.titre


class RedditDocument(Document) :
    """
    Classe fille représentant un document issu de Reddit
    """

    # Initialise un document Reddit avec le nombre de commentaires
    def __init__(self, titre, auteur, date, url, texte, nombre_commentaires) :
        super().__init__(titre, auteur, date, url, texte)
        self.nombre_commentaires = nombre_commentaires
        self.type_document = "Reddit"

    # Retourne le nombre de commentaires du post Reddit
    def get_nombre_commentaires(self) :
        return self.nombre_commentaires

    # Modifie le nombre de commentaires du post Reddit
    def set_nombre_commentaires(self, nombre) :
        self.nombre_commentaires = nombre

    # Retourne une représentation textuelle du document Reddit
    def __str__(self) :
        return f"[Reddit] {self.titre} ({self.nombre_commentaires} commentaires)"

    # Retourne le type du document
    def get_type(self) :
        return self.type_document


class ArxivDocument(Document) :
    """
    Classe fille représentant un document issu d'ArXiv
    """

    # Initialise un document ArXiv avec une liste d'auteurs
    def __init__(self, titre, auteurs, date, url, texte) :
        # Le premier auteur est considéré comme auteur principal
        auteur_principal = auteurs[0] if auteurs else "Inconnu"
        super().__init__(titre, auteur_principal, date, url, texte)
        self.co_auteurs = auteurs
        self.type_document = "Arxiv"

    # Retourne la liste des co-auteurs
    def get_co_auteurs(self) :
        return self.co_auteurs

    # Modifie la liste des co-auteurs
    def set_co_auteurs(self, auteurs) :
        self.co_auteurs = auteurs

    # Retourne une représentation textuelle du document ArXiv
    def __str__(self) :
        return f"[ArXiv] {self.titre} ({len(self.co_auteurs)} auteurs)"

    # Retourne le type du document
    def get_type(self) :
        return self.type_document
