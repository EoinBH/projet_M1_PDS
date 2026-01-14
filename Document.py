# Document.py
from datetime import datetime

class Document:
    """
    Classe mère représentant un document générique
    """

    def __init__(self, titre, auteur, date, url, texte):
        self.titre = titre
        self.auteur = auteur
        self.date = datetime.fromtimestamp(date) if date != 0 else None
        self.url = url
        self.texte = texte

    # Accesseurs
    def get_titre(self):
        return self.titre

    def get_auteur(self):
        return self.auteur

    def get_date(self):
        return self.date

    def get_url(self):
        return self.url

    def get_texte(self):
        return self.texte

    def __str__(self):
        return self.titre

class RedditDocument(Document):
    """
    Classe fille représentant un document issu de Reddit
    """

    def __init__(self, titre, auteur, date, url, texte, nb_comments):
        # Appel du constructeur de la classe mère
        super().__init__(titre, auteur, date, url, texte)
        self.nb_comments = nb_comments

    # Accesseur
    def get_nb_comments(self):
        return self.nb_comments

    # Mutateur
    def set_nb_comments(self, nb):
        self.nb_comments = nb

    def __str__(self):
        return (f"[Reddit] {self.titre} | "
                f"Auteur : {self.auteur} | "
                f"Commentaires : {self.nb_comments}")

class ArxivDocument(Document):
    """
    Classe fille représentant un document issu d'ArXiv
    """

    def __init__(self, titre, auteurs, date, url, texte):
        """
        auteurs : liste de noms d'auteurs
        """
        # Pour rester cohérent avec la classe mère,
        # on stocke le premier auteur comme auteur principal
        auteur_principal = auteurs[0] if auteurs else "Unknown"

        super().__init__(titre, auteur_principal, date, url, texte)

        self.co_auteurs = auteurs

    # Accesseur
    def get_co_auteurs(self):
        return self.co_auteurs

    # Mutateur
    def set_co_auteurs(self, auteurs):
        self.co_auteurs = auteurs

    def __str__(self):
        return (f"[ArXiv] {self.titre} | "
                f"Auteurs : {', '.join(self.co_auteurs)}")

