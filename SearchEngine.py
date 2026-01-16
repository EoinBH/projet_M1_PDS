# SearchEngine.py

import re
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix


class SearchEngine :
    """
    Moteur de recherche basé sur un corpus
    """

    # Initialise le moteur de recherche et construit le vocabulaire et les matrices
    def __init__(self, corpus) :
        self.corpus = corpus

        # Construction immédiate du vocabulaire et des matrices
        self.vocab = self._construire_vocabulaire()
        self.mat_TF = self._construire_matrice_tf()
        self.mat_TFxIDF = self._construire_matrice_tfidf()

    # Construit le vocabulaire à partir des documents du corpus
    def _construire_vocabulaire(self) :
        ensemble_vocabulaire = set()

        for document in self.corpus.id2doc.values() :
            texte_nettoye = self.corpus.nettoyer_texte(document.texte)
            mots = re.split(r"\s+", texte_nettoye)
            ensemble_vocabulaire.update(mots)

        liste_vocabulaire = sorted(ensemble_vocabulaire)

        vocabulaire = {}
        for indice, mot in enumerate(liste_vocabulaire) :
            vocabulaire[mot] = {
                "id" : indice,
                "TF" : 0,
                "DF" : 0
            }

        return vocabulaire

    # Construit la matrice de fréquences de termes (TF)
    def _construire_matrice_tf(self) :
        lignes, colonnes, donnees = [], [], []

        for identifiant_document, document in self.corpus.id2doc.items() :
            texte_nettoye = self.corpus.nettoyer_texte(document.texte)
            mots = re.split(r"\s+", texte_nettoye)

            compteur_mots = {}
            for mot in mots :
                compteur_mots[mot] = compteur_mots.get(mot, 0) + 1

            for mot, compte in compteur_mots.items() :
                id_colonne = self.vocab[mot]["id"]
                lignes.append(identifiant_document)
                colonnes.append(id_colonne)
                donnees.append(compte)

                self.vocab[mot]["TF"] += compte

            for mot in set(mots) :
                self.vocab[mot]["DF"] += 1

        matrice_tf = csr_matrix(
            (donnees, (lignes, colonnes)),
            shape=(len(self.corpus.id2doc), len(self.vocab)),
            dtype=float
        )

        return matrice_tf

    # Construit la matrice pondérée TFxIDF :
    # La matrice TF-IDF permet de pondérer les mots d’un document en fonction de leur importance réelle dans le corpus,
    # en favorisant les termes rares et informatifs et en pénalisant les mots trop fréquents,
    # ce qui améliore fortement la pertinence des résultats de recherche.
    def _construire_matrice_tfidf(self) :
        # L’IDF pénalise les mots trop fréquents et peu discriminants
        nombre_documents = self.mat_TF.shape[0]
        vecteur_idf = np.zeros(len(self.vocab))

        for mot, informations in self.vocab.items() :
            df = informations["DF"]
            if df > 0 :
                # Formule mathématique de l’IDF :
                vecteur_idf[informations["id"]] = np.log(nombre_documents / df)
                # Mot très fréquent dans le corpus → DF grand → IDF petit
                # Mot rare → DF petit → IDF grand
                # Le log sert à éviter des valeurs trop grandes et à lisser l’impact des mots très rares

        return self.mat_TF.multiply(vecteur_idf)

    # Transforme une requête textuelle en vecteur du vocabulaire
    def _requete_vers_vecteur(self, requete) :
        requete_nettoyee = self.corpus.nettoyer_texte(requete)
        mots = re.split(r"\s+", requete_nettoyee)

        colonnes, donnees = [], []
        for mot in mots :
            if mot in self.vocab :
                colonnes.append(self.vocab[mot]["id"])
                donnees.append(1)

        if not colonnes :
            return None

        return csr_matrix(
            (donnees, ([0] * len(colonnes), colonnes)),
            shape=(1, len(self.vocab)),
            dtype=float
        )

    # Calcule la similarité cosinus entre la requête et tous les documents
    # Au lieu de comparer des textes mot par mot, on :
    # transforme les documents en vecteurs numériques
    # transforme la requête en vecteur
    # mesure leur proximité mathématique
    # Le cosinus mesure l’angle, pas la longueur
    def _similarite_cosinus(self, vecteur_requete) :
        scores = self.mat_TFxIDF.dot(vecteur_requete.T).toarray().flatten()

        normes_documents = np.sqrt(self.mat_TFxIDF.power(2).sum(axis=1)).A1
        norme_requete = np.sqrt(vecteur_requete.power(2).sum())

        with np.errstate(divide="ignore", invalid="ignore") :
            similarites = scores / (normes_documents * norme_requete)
            similarites[np.isnan(similarites)] = 0.0

        return similarites

    # Recherche les documents les plus pertinents pour une requête donnée
    def search(self, requete, top_n=5) :
        vecteur_requete = self._requete_vers_vecteur(requete)
        if vecteur_requete is None :
            return pd.DataFrame()

        scores = self._similarite_cosinus(vecteur_requete)
        meilleurs_ids = np.argsort(scores)[::-1][:top_n]

        resultats = []
        for identifiant_document in meilleurs_ids :
            if scores[identifiant_document] > 0 :
                document = self.corpus.id2doc[identifiant_document]
                resultats.append({
                    "score" : scores[identifiant_document],
                    "titre" : document.titre,
                    "auteur" : document.auteur,
                    "source" : document.get_type()
                })

        return pd.DataFrame(resultats)
