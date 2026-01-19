# Corpus.py

import re
import pandas as pd
from Document import Document
from Author import Auteur


class Corpus :
    """
    Classe représentant un corpus de documents
    """

    _instance = None  # Attribut de classe pour le Singleton

    # Implémente le pattern Singleton
    def __new__(cls, nom) :
        if cls._instance is None :
            cls._instance = super(Corpus, cls).__new__(cls)
        return cls._instance

    # Initialise le corpus (une seule fois avec le Singleton)
    def __init__(self, nom) :
        if not hasattr(self, "initialise") :
            self.nom = nom
            self.auteurs = {}          # dictionnaire nom -> Auteur
            self.id2doc = {}           # dictionnaire id -> Document
            self.nombre_documents = 0
            self.nombre_auteurs = 0
            self.initialise = True

    # Ajoute un document au corpus et met à jour les auteurs
    def add_document(self, document) :
        identifiant_document = self.nombre_documents
        self.id2doc[identifiant_document] = document
        self.nombre_documents += 1

        nom_auteur = document.auteur

        if nom_auteur not in self.auteurs :
            self.auteurs[nom_auteur] = Auteur(nom_auteur)
            self.nombre_auteurs += 1

        self.auteurs[nom_auteur].ajouter_document(
            identifiant_document,
            document
        )

        if hasattr(self, "_texte_complet"):
            del self._texte_complet

    # Affiche les documents triés par date
    def show_by_date(self, n=5) :
        documents = [d for d in self.id2doc.values() if d.date is not None]
        documents.sort(key=lambda d : d.date)

        for document in documents[:n] :
            print(document.date, "-", document)

    # Affiche les documents triés par titre
    def show_by_title(self, n=5) :
        documents = list(self.id2doc.values())
        documents.sort(key=lambda d : d.titre.lower())

        for document in documents[:n] :
            print(document.titre)

    # Retourne une représentation synthétique du corpus
    def __repr__(self) :
        return (
            f"Corpus '{self.nom}' | "
            f"{self.nombre_documents} documents | "
            f"{self.nombre_auteurs} auteurs"
        )

    # Sauvegarde le corpus dans un fichier CSV
    def save(self, nom_fichier) :
        donnees = []

        for identifiant_document, document in self.id2doc.items() :
            donnees.append({
                "id" : identifiant_document,
                "titre" : document.titre,
                "auteur" : document.auteur,
                "date" : document.date.timestamp() if document.date else 0,
                "url" : document.url,
                "texte" : document.texte
            })

        dataframe = pd.DataFrame(donnees)
        dataframe.to_csv(nom_fichier, index=False)

    # Charge un corpus depuis un fichier CSV
    @classmethod
    def load(cls, nom_fichier, nom, reload=True):
        corpus = cls(nom)

        if reload:
            corpus.reload(nom)

        dataframe = pd.read_csv(nom_fichier)

        for _, ligne in dataframe.iterrows():
            document = Document(
                titre=ligne["titre"],
                auteur=ligne["auteur"],
                date=ligne["date"],
                url=ligne["url"],
                texte=ligne["texte"]
            )
            corpus.add_document(document)

        return corpus

    # Remplace complètement le contenu par un nouveau corpus
    # Il s'agit d'méthode explicite de réinitialisation permettant de
    # vider et recharger proprement les données, tout en conservant l’unicité de l’instance (Singleton)
    def reload(self, nom=None) :
        self.nom = nom if nom else self.nom
        self.auteurs = {}
        self.id2doc = {}
        self.nombre_documents = 0
        self.nombre_auteurs = 0

        if hasattr(self, "_texte_complet"):
            del self._texte_complet
    
    # Construit et mémorise le texte global du corpus
    def _construire_texte_complet(self) :
        if not hasattr(self, "_texte_complet") :
            self._texte_complet = " ".join(
                document.texte for document in self.id2doc.values()
            )

    # Recherche toutes les occurrences d’un mot-clé dans le corpus
    def search(self, mot_cle) :
        self._construire_texte_complet()

        motif = re.compile(mot_cle, re.IGNORECASE)
        correspondances = []

        for match in motif.finditer(self._texte_complet) :
            correspondances.append({
                "match" : match.group(),
                "start" : match.start(),
                "end" : match.end()
            })

        return correspondances

    # Construit un concordancier pour une expression donnée
    def concorde(self, expression, taille_contexte=30) :
        self._construire_texte_complet()

        motif = re.compile(expression, re.IGNORECASE)
        donnees = []

        for match in motif.finditer(self._texte_complet) :
            debut, fin = match.start(), match.end()

            contexte_gauche = self._texte_complet[max(0, debut - taille_contexte) : debut]
            contexte_droit = self._texte_complet[fin : fin + taille_contexte]

            donnees.append({
                "contexte_gauche" : contexte_gauche,
                "motif" : match.group(),
                "contexte_droit" : contexte_droit
            })

        return pd.DataFrame(donnees)

    # Nettoie un texte pour l’analyse linguistique
    def nettoyer_texte(self, texte) :
        texte = texte.lower()
        texte = texte.replace("\n", " ")

        texte = re.sub(r"\d+", " ", texte)
        texte = re.sub(r"[^\w\s]", " ", texte)
        texte = re.sub(r"\s+", " ", texte)

        return texte.strip()

    # Affiche des statistiques textuelles globales du corpus
    def stats(self, n=10) :
        self._construire_texte_complet()

        texte_nettoye = self.nettoyer_texte(self._texte_complet)
        mots = texte_nettoye.split(" ")

        frequences = {}
        for mot in mots :
            if mot :
                frequences[mot] = frequences.get(mot, 0) + 1

        print(f"Nombre de mots différents : {len(frequences)}")
        print(f"\nTop {n} mots les plus fréquents :")

        mots_tries = sorted(
            frequences.items(),
            key=lambda x : x[1],
            reverse=True
        )

        for mot, compte in mots_tries[:n] :
            print(f"{mot} : {compte}")

    # Construit le vocabulaire du corpus
    def construire_vocabulaire(self) :
        ensemble_vocabulaire = set()

        for document in self.id2doc.values() :
            texte_nettoye = self.nettoyer_texte(document.texte)
            mots = re.split(r"\s+", texte_nettoye)
            ensemble_vocabulaire.update(mot for mot in mots if mot)

        return {mot : 0 for mot in ensemble_vocabulaire}

    # Calcule les fréquences TF et DF pour chaque mot du corpus
    def compute_frequencies(self) :
        vocabulaire = self.construire_vocabulaire()
        frequences_documents = {mot : 0 for mot in vocabulaire}

        for document in self.id2doc.values() :
            texte_nettoye = self.nettoyer_texte(document.texte)
            mots = [mot for mot in texte_nettoye.split(" ") if mot]

            for mot in mots :
                vocabulaire[mot] += 1

            for mot in set(mots) :
                frequences_documents[mot] += 1

        dataframe = pd.DataFrame({
            "mot" : list(vocabulaire.keys()),
            "TF" : list(vocabulaire.values()),
            "DF" : [frequences_documents[mot] for mot in vocabulaire.keys()]
        })

        dataframe = dataframe.sort_values(
            by="TF",
            ascending=False
        ).reset_index(drop=True)

        return dataframe
