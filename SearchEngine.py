import re
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix

class SearchEngine:
    """
    Moteur de recherche basé sur un corpus
    """

    def __init__(self, corpus):
        """
        corpus : instance de Corpus
        """
        self.corpus = corpus

        # Construction immédiate du vocabulaire et des matrices
        self.vocab = self._build_vocab()
        self.mat_TF = self._build_tf_matrix()
        self.mat_TFxIDF = self._build_tfidf_matrix()

    def _build_vocab(self):
        vocab_set = set()

        for doc in self.corpus.id2doc.values():
            texte = self.corpus.nettoyer_texte(doc.texte)
            mots = re.split(r"\s+", texte)
            vocab_set.update(mots)

        vocab_list = sorted(vocab_set)

        vocab = {}
        for idx, mot in enumerate(vocab_list):
            vocab[mot] = {
                "id": idx,
                "TF": 0,
                "DF": 0
            }

        return vocab

    def _build_tf_matrix(self):
        rows, cols, data = [], [], []

        for doc_id, doc in self.corpus.id2doc.items():
            texte = self.corpus.nettoyer_texte(doc.texte)
            mots = re.split(r"\s+", texte)

            counts = {}
            for mot in mots:
                counts[mot] = counts.get(mot, 0) + 1

            for mot, count in counts.items():
                col_id = self.vocab[mot]["id"]
                rows.append(doc_id)
                cols.append(col_id)
                data.append(count)

                self.vocab[mot]["TF"] += count

            for mot in set(mots):
                self.vocab[mot]["DF"] += 1

        mat_TF = csr_matrix(
            (data, (rows, cols)),
            shape=(len(self.corpus.id2doc), len(self.vocab)),
            dtype=float
        )

        return mat_TF
    
    def _build_tfidf_matrix(self):
        n_docs = self.mat_TF.shape[0]
        idf = np.zeros(len(self.vocab))

        for mot, info in self.vocab.items():
            df = info["DF"]
            if df > 0:
                idf[info["id"]] = np.log(n_docs / df)

        return self.mat_TF.multiply(idf)
    
    def _query_to_vector(self, query):
        query = self.corpus.nettoyer_texte(query)
        mots = re.split(r"\s+", query)

        cols, data = [], []
        for mot in mots:
            if mot in self.vocab:
                cols.append(self.vocab[mot]["id"])
                data.append(1)

        if not cols:
            return None

        return csr_matrix(
            (data, ([0]*len(cols), cols)),
            shape=(1, len(self.vocab)),
            dtype=float
        )

    def _cosine_similarity(self, vecteur_query):
        scores = self.mat_TFxIDF.dot(vecteur_query.T).toarray().flatten()

        norms_docs = np.sqrt(self.mat_TFxIDF.power(2).sum(axis=1)).A1
        norm_query = np.sqrt(vecteur_query.power(2).sum())

        with np.errstate(divide="ignore", invalid="ignore"):
            sim = scores / (norms_docs * norm_query)
            sim[np.isnan(sim)] = 0.0

        return sim
    
    def search(self, query, top_n=5):
        """
        Recherche des documents pertinents
        Retourne un DataFrame pandas
        """
        vecteur_query = self._query_to_vector(query)
        if vecteur_query is None:
            return pd.DataFrame()

        scores = self._cosine_similarity(vecteur_query)
        top_ids = np.argsort(scores)[::-1][:top_n]

        results = []
        for doc_id in top_ids:
            if scores[doc_id] > 0:
                doc = self.corpus.id2doc[doc_id]
                results.append({
                    "score": scores[doc_id],
                    "titre": doc.titre,
                    "auteur": doc.auteur,
                    "source": doc.getType()
                })

        return pd.DataFrame(results)



