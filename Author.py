# Author.py

class Author:
    """
    Classe représentant un auteur et sa production
    """

    def __init__(self, name):
        self.name = name
        self.ndoc = 0
        self.production = {}

    def add(self, doc_id, document):
        """
        Ajoute un document à la production de l'auteur
        """
        self.production[doc_id] = document
        self.ndoc += 1

    def taille_moyenne_documents(self):
        """
        Calcule la taille moyenne des documents (en nombre de mots)
        """
        if self.ndoc == 0:
            return 0

        total = 0
        for doc in self.production.values():
            total += len(doc.texte.split())

        return total / self.ndoc

    def __str__(self):
        return f"Auteur : {self.name} | Nombre de documents : {self.ndoc}"