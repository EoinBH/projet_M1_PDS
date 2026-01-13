from datetime import datetime
class Document() :

    # Constructeur :
    def __init__(self, titre, auteur, date, url, texte) :
        self.titre = titre
        self.auteur = auteur
        self.date = date #format timestamp
        self.url = url
        self.texte = texte

    # Récupérer le titre :
    def recupererTitre(self) :
        return self.titre
    
    # Récupérer l'auteur :
    def recupererAuteur(self) :
        return self.auteur

    # Récupérer la date :
    def recupererDate(self) :
        return self.date
    
    # Recuperer l'URL:
    def recupererURL(self) :
        return self.url
    
    # Recuperer le texte:
    def recupererTexte(self) :
        return self.texte
    
    def recupererDateUTC(self) :
        return datetime.fromtimestamp(self.date)
        
    def toutAfficher(self) :
        # Afficher toutes les informations :
        print(f"Titre : {self.recupererTitre()}")
        print(f"Auteur : {self.recupererAuteur()}")
        print(f"Date : {self.recupererDate()}")
        print(f"URL : {self.recupererURL()}")
        print(f"Texte : {self.recupererTexte()}")
    
    def __str__(self) :
        # Afficher une version 'digeste'
        print(f"Titre : {self.recupererTitre()}", end = ", ")
        print(f"URL : {self.recupererURL()}")
