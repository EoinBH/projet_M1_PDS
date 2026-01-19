import pandas as pd
import re
import tkinter as tk
from tkinter import ttk
from datetime import datetime

from Corpus import Corpus
from Document import Document
from SearchEngine import SearchEngine

# -----------------------------
# Prétraitement
# -----------------------------

def decouper_en_phrases(texte) :
    phrases = re.split(r"[.!?]+", texte)
    # On utilise le seuil > 20 pour éviter les phrases trop courtes ou bruitées
    return [p.strip() for p in phrases if len(p.strip()) > 20]

def construire_corpus() :
    df = pd.read_csv("./discours_US.csv", sep="\t")
    print(df.head())
    print(df.columns)

    distribution_auteurs = df["speaker"].value_counts()
    print(distribution_auteurs.head(10))

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

    # Tests 
    requetes = ["freedom", "economy", "healthcare", "war"]
    moteur = SearchEngine(corpus)
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
    corpus = construire_corpus()
    moteur = SearchEngine(corpus)
    lancer_interface(moteur)


if __name__ == "__main__":
    main()