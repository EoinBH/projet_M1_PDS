# Document.py
from datetime import datetime

class Document:
    """
    Classe représentant un document textuel avec ses métadonnées
    """

    def __init__(self, titre, auteur, date, url, texte):
        self.titre = titre
        self.auteur = auteur
        # date attendue sous forme timestamp
        self.date = datetime.fromtimestamp(date)
        self.url = url
        self.texte = texte

    def afficher(self):
        """Affiche toutes les informations du document"""
        print("Titre :", self.titre)
        print("Auteur :", self.auteur)
        print("Date :", self.date)
        print("URL :", self.url)
        print("Texte :", self.texte)

    def __str__(self):
        """Version digeste du document"""
        return self.titre
