# main.py

import praw
import urllib.request
import xmltodict
import ssl
import certifi
import pandas as pd
import tkinter as tk
from tkinter import ttk
import re
from datetime import datetime
from tabulate import tabulate

from Document import Document, RedditDocument, ArxivDocument
from Corpus import Corpus
from DocumentFactory import DocumentFactory
from SearchEngine import SearchEngine


# -------------------------
# Configuration Reddit
# -------------------------
reddit = praw.Reddit(
    client_id="IDNxqb2cDUV0GxAlAUjplA",
    client_secret="A6Ar2mi-4xNnhSmTNRaxSSosngWIig",
    user_agent="InfoApp"
)


# Construit un corpus à partir de sources Reddit et ArXiv selon un thème donné
def construire_corpus(theme, nombre_max_posts) :
    corpus = Corpus(theme)

    # -------- Reddit --------
    subreddit = reddit.subreddit(theme)

    for post in subreddit.hot(limit=nombre_max_posts) :
        texte = post.title + ". " + post.selftext
        texte = texte.replace("\n", " ").replace("\r", " ")

        if len(texte) < 20 :
            continue

        document = DocumentFactory.creer_document(
            type_document="Reddit",
            titre=post.title,
            auteur=str(post.author),
            date=post.created_utc,
            url=post.url,
            texte=texte,
            nombre_commentaires=post.num_comments
        )

        corpus.add_document(document)

    # -------- ArXiv --------
    url_api = (
        f"http://export.arxiv.org/api/query?"
        f"search_query=all:{theme}&start=0&max_results={nombre_max_posts}"
    )

    contexte_ssl = ssl.create_default_context(cafile=certifi.where())
    reponse = urllib.request.urlopen(url_api, context=contexte_ssl)
    donnees = xmltodict.parse(reponse.read())

    entrees = donnees["feed"].get("entry", [])
    if isinstance(entrees, dict) :
        entrees = [entrees]

    for entree in entrees :
        texte = entree["title"] + ". " + entree["summary"]
        texte = texte.replace("\n", " ").replace("\r", " ")

        if len(texte) < 20 :
            continue

        auteurs = entree["author"]
        if isinstance(auteurs, dict) :
            noms_auteurs = [auteurs["name"]]
        else :
            noms_auteurs = [a["name"] for a in auteurs]

        for auteur in noms_auteurs :
            document = DocumentFactory.creer_document(
                type_document="Arxiv",
                titre=entree["title"],
                auteurs=auteur,
                date=0,
                url=entree["id"],
                texte=texte
            )

            corpus.add_document(document)

    return corpus

# Effectuer des tests sur le code
def tests_complets() :
    corpus = construire_corpus("jazz", 2000)

    print(corpus)

    print("\nDocuments triés par date :")
    corpus.show_by_date(5)

    print("\nDocuments triés par titre :")
    corpus.show_by_title(5)

    # Sauvegarde du corpus
    corpus.save("corpus.csv")

    # Chargement du corpus sauvegardé
    corpus_recharge = Corpus.load("corpus.csv", "jazz_reloaded")
    print("\nCorpus rechargé :", corpus_recharge)

    # -------------------------
    # Tests des classes filles
    # -------------------------
    document_reddit = RedditDocument(
        titre="Great jazz album",
        auteur="user123",
        date=1700000000,
        url="https://reddit.com/...",
        texte="This album is amazing",
        nombre_commentaires=42
    )

    document_arxiv = ArxivDocument(
        titre="Topology and Jazz",
        auteurs=["Octavio A. Agustín-Aquino", "Guerino Mazzola"],
        date=0,
        url="http://arxiv.org/abs/1234.5678",
        texte="This paper explores..."
    )

    corpus_recharge.add_document(document_reddit)
    corpus_recharge.add_document(document_arxiv)

    for document in corpus_recharge.id2doc.values() :
        print(document.get_type(), "→", document)

    # -------------------------
    # Test du Singleton Corpus
    # -------------------------
    corpus_1 = Corpus("JazzCorpus")
    corpus_2 = Corpus("AutreNom")

    if id(corpus_1) == id(corpus_2) :
        print("Singleton marche, les deux variables contiennent la même instance.")
    else :
        print("Singleton ne marche pas, les deux variables contiennent des instances différentes.")

    # -------------------------
    # Tests de DocumentFactory
    # -------------------------
    corpus_test = Corpus("Factory_Test")

    document_reddit = DocumentFactory.creer_document(
        type_document="Reddit",
        titre="Great jazz album",
        auteur="user123",
        date=1700000000,
        url="https://reddit.com/...",
        texte="This album is amazing",
        nombre_commentaires=42
    )

    document_arxiv = DocumentFactory.creer_document(
        type_document="Arxiv",
        titre="Topology and Jazz",
        auteurs=["Octavio A. Agustín-Aquino", "Guerino Mazzola"],
        date=0,
        url="http://arxiv.org/abs/1234.5678",
        texte="This paper explores..."
    )

    corpus_test.add_document(document_reddit)
    corpus_test.add_document(document_arxiv)

    for document in corpus_test.id2doc.values() :
        print(document.get_type(), "→", document)

    # -------------------------
    # Tests de recherche textuelle
    # -------------------------
    resultats = corpus.search("jazz")
    print("Occurrences trouvées :", len(resultats))

    concordancier = corpus.concorde("jazz", taille_contexte=20)
    print(concordancier.head())

    # -------------------------
    # Statistiques et fréquences
    # -------------------------
    corpus.stats(10)

    table_frequences = corpus.compute_frequencies()
    print("Top 10 mots les plus fréquents (TF) :")
    print(table_frequences.head(10))

    # -------------------------
    # Tests du moteur de recherche
    # -------------------------
    moteur = SearchEngine(corpus)

    vocabulaire = moteur.vocab
    print(f"Nombre de mots dans le vocabulaire : {len(vocabulaire)}")

    matrice_tf = moteur.mat_TF
    print(f"Matrice TF shape : {matrice_tf.shape}")

    matrice_tfidf = moteur.mat_TFxIDF
    print(f"Matrice TFxIDF shape : {matrice_tfidf.shape}")

    resultats_recherche = moteur.search("jazz harmony", top_n=5)
    print(tabulate(resultats_recherche, headers="keys"))

    resultats_recherche = moteur.search_avec_progression("improvisation", top_n=5)
    print(tabulate(resultats_recherche, headers="keys"))
    
    requetes = ["freedom", "economy", "healthcare", "war"]
    for req in requetes :
        # Tests de search
        print(f"\nRecherche pour : '{req}'")
        resultats = corpus.search(req)
        print("Nombre d'occurrences :", len(resultats))

        # Test de concorde
        concordancier = corpus.concorde(req, taille_contexte=40)
        print(concordancier.head())

        # Test du moteur de recherche avec progression
        resultats = moteur.search_avec_progression(req, top_n=5)
        if resultats.empty:
            print("Aucun résultat trouvé.")
        else:
            print(resultats)

# -----------------------------
# Prétraitement
# -----------------------------

def decouper_en_phrases(texte) :
    phrases = re.split(r"[.!?]+", texte)
    # On utilise le seuil > 20 pour éviter les phrases trop courtes ou bruitées
    return [p.strip() for p in phrases if len(p.strip()) > 20]

def construire_corpus_discours() :
    df = pd.read_csv("./discours_US.csv", sep="\t")
    #print(df.head())
    #print(df.columns)

    distribution_auteurs = df["speaker"].value_counts()
    #print(distribution_auteurs.head(10))

    corpus = Corpus("Discours_US")
    # Test reload
    #corpus.reload("Discours_US")

    for _, ligne in df.iterrows():
        auteur = ligne["speaker"]
        texte_discours = ligne["text"]
        date_str = ligne["date"]
        url = ligne["link"]

        # Conversion de la date (ex : "April 12, 2015")
        try:
            date = datetime.strptime(date_str, "%B %d, %Y").timestamp()
        except Exception:
            date = 0

        phrases = decouper_en_phrases(texte_discours)

        for phrase in phrases:
            document = Document(
                titre="Discours US",
                auteur=auteur,
                date=date,
                url=url,
                texte=phrase
            )
            corpus.add_document(document)
    
    return corpus

# -----------------------------
# Interface Tkinter
# -----------------------------

def lancer_interface(moteur):
    fenetre = tk.Tk()
    fenetre.title("Moteur de recherche - Discours US")
    fenetre.geometry("1000x600")

    # ----- Widgets -----

    tk.Label(fenetre, text="Mots clefs :", font=("Aptos", 11)).pack(anchor="w")
    entree_requete = tk.Entry(fenetre, width=60)
    entree_requete.pack(fill="x", padx=5)

    tk.Label(fenetre, text="Nombre de résultats :", font=("Aptos", 11)).pack(anchor="w")
    slider_top_n = tk.Scale(fenetre, from_=1, to=20, orient=tk.HORIZONTAL)
    slider_top_n.set(5)
    slider_top_n.pack(anchor="w", padx=5)

    # ----- Filtres -----

    cadre_filtres = tk.LabelFrame(fenetre, text="Filtres", font=("Aptos", 11), padx=5, pady=5)
    cadre_filtres.pack(fill="x", padx=5, pady=5)

    tk.Label(cadre_filtres, text="Auteur :", font=("Aptos", 11)).grid(row=0, column=0, sticky="w")
    entree_auteur = tk.Entry(cadre_filtres, width=30)
    entree_auteur.grid(row=0, column=1, padx=5)

    tk.Label(cadre_filtres, text="Année minimale :", font=("Aptos", 11)).grid(row=0, column=2, sticky="w")
    entree_annee = tk.Entry(cadre_filtres, width=10)
    entree_annee.grid(row=0, column=3, padx=5)

    # ----- Zone résultats -----

    zone_resultats = tk.Text(fenetre, height=25, width=120)
    zone_resultats.pack(padx=5, pady=5, fill="both", expand=True)

    # ----- Fonction de recherche -----

    def rechercher():
        requete = entree_requete.get()
        top_n = slider_top_n.get()
        auteur_filtre = entree_auteur.get().strip().lower()
        annee_filtre = entree_annee.get().strip()

        zone_resultats.delete("1.0", tk.END)

        if not requete:
            zone_resultats.insert(tk.END, "Veuillez entrer une requête.\n")
            return

        resultats = moteur.search(requete, top_n=top_n)

        if resultats.empty:
            zone_resultats.insert(tk.END, "Aucun résultat trouvé.\n")
            return

        # Filtre auteur
        if auteur_filtre:
            resultats = resultats[
                resultats["auteur"].str.lower().str.contains(auteur_filtre)
            ]

        # Filtre année
        if annee_filtre.isdigit():
            annee_min = int(annee_filtre)
            resultats = resultats[
                resultats["titre"].notnull()  # sécurité
            ]

        if resultats.empty:
            zone_resultats.insert(tk.END, "Aucun résultat après filtrage.\n")
        else:
            zone_resultats.insert(
                tk.END,
                resultats.to_string(index=False)
            )

    # ----- Bouton -----

    bouton = tk.Button(
        fenetre,
        text="Rechercher",
        command=rechercher,
        bg="#4CAF50",
        fg="black",
        font=("Aptos", 11, "bold")
    )
    bouton.pack(pady=5)

    fenetre.mainloop()

# -----------------------------
# Main
# -----------------------------
def main():
    print("Choisissez le mode d'exécution :")
    print("1 : Mode Test (affiche tous les tests dans la console)")
    print("2 : Mode Interface (interface Tkinter interactive)")

    choix = input("Entrez 1 ou 2 : ").strip()

    if choix == "2":
        corpus = construire_corpus_discours()
        moteur = SearchEngine(corpus)
        lancer_interface(moteur)
    else:
        tests_complets()

if __name__ == "__main__" :
    main()
