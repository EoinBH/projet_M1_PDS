# Corpus.py
import re
import pandas as pd
from Document import Document
from Author import Author

class Corpus:
    """
    Classe représentant un corpus de documents
    """

    _instance = None  # attribut de classe

    def __new__(cls, nom):
        if cls._instance is None:
            cls._instance = super(Corpus, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, nom):
        # Évite de réinitialiser si déjà créé
        if not hasattr(self, "initialized"):
            self.nom = nom
            self.authors = {}     # dictionnaire name -> Author
            self.id2doc = {}      # dictionnaire id -> Document
            self.ndoc = 0
            self.naut = 0
            self.initialized = True

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
        return f"Corpus '{self.nom}' | {self.ndoc} documents | {self.naut} auteurs"

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
    
    def _build_full_text(self):
        """
        Construit une seule fois la chaîne concaténant tous les textes du corpus
        """
        if not hasattr(self, "_full_text"):
            self._full_text = " ".join(
                doc.texte for doc in self.id2doc.values()
            )

    def search(self, keyword):
        """
        Retourne les passages contenant le mot-clef
        """
        self._build_full_text()

        motif = re.compile(keyword, re.IGNORECASE)
        matches = []

        for m in motif.finditer(self._full_text):
            matches.append({
                "match": m.group(),
                "start": m.start(),
                "end": m.end()
            })

        return matches
    
    def concorde(self, expression, context_size=30):
        """
        Construit un concordancier pour une expression donnée
        """
        self._build_full_text()

        motif = re.compile(expression, re.IGNORECASE)
        data = []

        for m in motif.finditer(self._full_text):
            start, end = m.start(), m.end()

            left_context = self._full_text[max(0, start - context_size):start]
            right_context = self._full_text[end:end + context_size]

            data.append({
                "contexte_gauche": left_context,
                "motif": m.group(),
                "contexte_droit": right_context
            })

        return pd.DataFrame(data)
    
    def nettoyer_texte(self, texte):
        """
        Nettoie une chaîne de caractères :
        - minuscules
        - suppression des retours à la ligne
        - suppression de la ponctuation
        - suppression des chiffres
        """
        texte = texte.lower()
        texte = texte.replace("\n", " ")

        # Suppression des chiffres
        texte = re.sub(r"\d+", " ", texte)

        # Suppression de la ponctuation
        texte = re.sub(r"[^\w\s]", " ", texte)

        # Suppression des espaces multiples
        texte = re.sub(r"\s+", " ", texte)

        return texte.strip()

    def stats(self, n=10):
        """
        Affiche des statistiques textuelles sur le corpus
        """
        self._build_full_text()

        # Nettoyage du texte global
        texte_nettoye = self.nettoyer_texte(self._full_text)

        # Tokenisation simple
        mots = texte_nettoye.split(" ")

        # Fréquences
        freq = {}
        for mot in mots:
            if mot:
                freq[mot] = freq.get(mot, 0) + 1

        # Nombre de mots différents
        vocabulaire = len(freq)

        print(f"Nombre de mots différents : {vocabulaire}")
        print(f"\nTop {n} mots les plus fréquents :")

        # Tri par fréquence décroissante
        mots_tries = sorted(freq.items(), key=lambda x: x[1], reverse=True)

        for mot, count in mots_tries[:n]:
            print(f"{mot} : {count}")

    def build_vocab(self):
        """
        Construit le vocabulaire du corpus
        """
        vocab_set = set()

        for doc in self.id2doc.values():
            texte_nettoye = self.nettoyer_texte(doc.texte)

            # Découpage en mots par espaces et ponctuation
            mots = re.split(r"\s+|[.,;:!?()\[\]\"']", texte_nettoye)

            # Ajout des mots non vides au vocabulaire
            mots = [mot for mot in mots if mot]
            vocab_set.update(mots)

        # On retourne un dictionnaire avec valeur initiale 0 pour chaque mot
        vocab = {mot: 0 for mot in vocab_set}

        return vocab
    
    def compute_frequencies(self):
        """
        Construit un tableau pandas contenant :
        - TF : nombre total d'occurrences de chaque mot
        - DF : nombre de documents contenant chaque mot
        """
        vocab = self.build_vocab()

        # Initialisation du compteur de document frequency
        df_counts = {mot: 0 for mot in vocab}

        # Parcours des documents
        for doc in self.id2doc.values():
            texte_nettoye = self.nettoyer_texte(doc.texte)
            mots = re.split(r"\s+|[.,;:!?()\[\]\"']", texte_nettoye)
            mots = [mot for mot in mots if mot]

            # Compter occurrences (TF)
            for mot in mots:
                vocab[mot] += 1

            # Compter document frequency (DF)
            mots_uniques = set(mots)
            for mot in mots_uniques:
                df_counts[mot] += 1

        # Création du DataFrame final
        freq_df = pd.DataFrame({
            "mot": list(vocab.keys()),
            "TF": list(vocab.values()),
            "DF": [df_counts[mot] for mot in vocab.keys()]
        })

        # Tri par TF décroissante
        freq_df = freq_df.sort_values(by="TF", ascending=False).reset_index(drop=True)

        return freq_df






