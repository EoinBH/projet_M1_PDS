# main.py
import praw
import urllib.request
import xmltodict
import ssl
import certifi

from Document import Document
from Author import Author

# -------------------------
# Configuration Reddit
# -------------------------
reddit = praw.Reddit(
    client_id='IDNxqb2cDUV0GxAlAUjplA',
    client_secret='A6Ar2mi-4xNnhSmTNRaxSSosngWIig',
    user_agent='InfoApp')

# -------------------------
# Récupération des données
# -------------------------
def recupererDonnees(theme, maxPosts):
    id2doc = {}
    id2aut = {}

    current_id = 0

    # -------- Reddit --------
    subreddit = reddit.subreddit(theme)

    for post in subreddit.hot(limit=maxPosts):
        texte = post.title + ". " + post.selftext
        texte = texte.replace("\n", " ").replace("\r", " ")

        if len(texte) < 20:
            continue

        auteur = str(post.author)

        doc = Document(
            titre=post.title,
            auteur=auteur,
            date=post.created_utc,
            url=post.url,
            texte=texte
        )

        id2doc[current_id] = doc

        # Gestion des auteurs
        if auteur not in id2aut:
            id2aut[auteur] = Author(auteur)

        id2aut[auteur].add(current_id, doc)

        current_id += 1

    # -------- ArXiv --------
    url = f"http://export.arxiv.org/api/query?search_query=all:{theme}&start=0&max_results={maxPosts}"
    context = ssl.create_default_context(cafile=certifi.where())
    response = urllib.request.urlopen(url, context=context)
    data = xmltodict.parse(response.read())

    entries = data['feed'].get('entry', [])
    if isinstance(entries, dict):
        entries = [entries]

    for entry in entries:
        texte = entry['title'] + ". " + entry['summary']
        texte = texte.replace("\n", " ").replace("\r", " ")

        if len(texte) < 20:
            continue

        authors = entry['author']

        # Cas 1 : un seul auteur
        if isinstance(authors, dict):
            author_names = [authors['name']]
        # Cas 2 : plusieurs auteurs
        elif isinstance(authors, list):
            author_names = [a['name'] for a in authors]
        # Sécurité (au cas où)
        else:
            author_names = ["Unknown"]

        for auteur in author_names:
            doc = Document(
                titre=entry['title'],
                auteur=auteur,
                date=0,
                url=entry['id'],
                texte=texte
            )

        id2doc[current_id] = doc

        if auteur not in id2aut:
            id2aut[auteur] = Author(auteur)

        id2aut[auteur].add(current_id, doc)

        current_id += 1

    return id2doc, id2aut

# -------------------------
# Statistiques auteur
# -------------------------
def stats_auteur(id2aut):
    nom = input("Nom de l'auteur : ")

    if nom not in id2aut:
        print("Auteur inconnu.")
        return

    auteur = id2aut[nom]
    print(auteur)
    print("Taille moyenne des documents :", auteur.taille_moyenne_documents(), "mots")

# -------------------------
# Programme principal
# -------------------------
def main():
    theme = "jazz"
    id2doc, id2aut = recupererDonnees(theme, 20)

    print("Nombre total de documents :", len(id2doc))
    print("Nombre total d'auteurs :", len(id2aut))
    print()

    stats_auteur(id2aut)

if __name__ == "__main__":
    main()