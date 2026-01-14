# Corpus.py
import pandas as pd
from Document import Document
from Author import Author

class Corpus:
    """
    Classe représentant un corpus de documents
    """

    def __init__(self, nom):
        self.nom = nom
        self.authors = {}     # dictionnaire name -> Author
        self.id2doc = {}      # dictionnaire id -> Document
        self.ndoc = 0
        self.naut = 0

    # -------------------------
    # Ajout d'un document
    # -------------------------
    def add_document(self, document):
        doc_id = self.ndoc
        self.id2doc[doc_id] = document
        self.ndoc += 1

        auteur = document.auteur

        if auteur not in self.authors:
            self.authors[auteur] = Author(auteur)
            self.naut += 1

        self.authors[auteur].add(doc_id, document)

    # -------------------------
    # Affichage trié par date
    # -------------------------
    def show_by_date(self, n=5):
        docs = list(self.id2doc.values())
        docs = [d for d in docs if d.date is not None]
        docs.sort(key=lambda d: d.date)

        for doc in docs[:n]:
            print(doc.date, "-", doc)

    # -------------------------
    # Affichage trié par titre
    # -------------------------
    def show_by_title(self, n=5):
        docs = list(self.id2doc.values())
        docs.sort(key=lambda d: d.titre.lower())

        for doc in docs[:n]:
            print(doc.titre)

    # -------------------------
    # Représentation digeste
    # -------------------------
    def __repr__(self):
        return (f"Corpus '{self.nom}' | "
                f"{self.ndoc} documents | "
                f"{self.naut} auteurs")

    # -------------------------
    # Sauvegarde du corpus
    # -------------------------
    def save(self, filename):
        data = []

        for doc_id, doc in self.id2doc.items():
            data.append({
                "id": doc_id,
                "titre": doc.titre,
                "auteur": doc.auteur,
                "date": doc.date.timestamp() if doc.date else 0,
                "url": doc.url,
                "texte": doc.texte
            })

        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)

    # -------------------------
    # Chargement du corpus
    # -------------------------
    @classmethod
    def load(cls, filename, nom):
        df = pd.read_csv(filename)
        corpus = cls(nom)

        for _, row in df.iterrows():
            doc = Document(
                titre=row["titre"],
                auteur=row["auteur"],
                date=row["date"],
                url=row["url"],
                texte=row["texte"]
            )
            corpus.add_document(doc)

        return corpus