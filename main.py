# main.py

import praw
import urllib.request
import xmltodict
import ssl
import certifi
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


# Point d'entrée principal du programme
def main() :
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


if __name__ == "__main__" :
    main()
