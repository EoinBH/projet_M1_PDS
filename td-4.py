import pandas as pd
import praw
from praw.models import MoreComments
import urllib, urllib.request
import xmltodict
import certifi
import ssl
from pathlib import Path
from Document import Document
from pprint import pprint
#from datetime import datetime

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
    current_id = 0

    # -------- Reddit --------
    subreddit = reddit.subreddit(theme)

    for post in subreddit.hot(limit=maxPosts):
        texte = post.title + ". " + post.selftext
        texte = texte.replace("\n", " ").replace("\r", " ")

        if len(texte) >= 20:
            doc = Document(
                titre=post.title,
                auteur=str(post.author),
                date=post.created_utc,
                url=post.url,
                texte=texte
            )
            id2doc[current_id] = doc
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

        if len(texte) >= 20:
            doc = Document(
                titre=entry['title'],
                auteur=entry['author']['name'],
                date=0,  # ArXiv ne fournit pas toujours un timestamp simple
                url=entry['id'],
                texte=texte
            )
            id2doc[current_id] = doc
            current_id += 1

    return id2doc

# -------------------------
# Programme principal
# -------------------------
def main():
    theme = "jazz"
    id2doc = recupererDonnees(theme, 20)

    print(f"Nombre de documents : {len(id2doc)}\n")

    # Exemple d'affichage
    for doc_id, doc in list(id2doc.items())[:3]:
        print(f"ID {doc_id} → {doc}")
        print()

if __name__ == "__main__":
    main()