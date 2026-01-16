# Author.py


class Auteur :
    """
    Classe représentant un auteur et sa production documentaire
    """

    # Initialise un auteur avec son nom et une production vide
    def __init__(self, nom) :
        self.nom = nom
        self.nombre_documents = 0
        self.production = {}

    # Ajoute un document à la production de l'auteur
    def ajouter_document(self, identifiant_document, document) :
        self.production[identifiant_document] = document
        self.nombre_documents += 1

    # Calcule la taille moyenne des documents de l'auteur (en nombre de mots)
    def taille_moyenne_documents(self) :
        if self.nombre_documents == 0 :
            return 0

        total_mots = 0
        for document in self.production.values() :
            total_mots += len(document.texte.split())

        return total_mots / self.nombre_documents

    # Retourne une représentation textuelle de l'auteur
    def __str__(self) :
        return (
            f"Auteur : {self.nom} | "
            f"Nombre de documents : {self.nombre_documents}"
        )
