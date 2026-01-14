# main.py
import praw
import urllib.request
import xmltodict
import ssl
import certifi

from Document import Document, RedditDocument, ArxivDocument
from Corpus import Corpus

# -------------------------
# Configuration Reddit
# -------------------------
reddit = praw.Reddit(
    client_id='IDNxqb2cDUV0GxAlAUjplA',
    client_secret='A6Ar2mi-4xNnhSmTNRaxSSosngWIig',
    user_agent='InfoApp')

# -------------------------
# Construction du corpus
# -------------------------
def construire_corpus(theme, maxPosts):
    corpus = Corpus(theme)

    # -------- Reddit --------
    subreddit = reddit.subreddit(theme)

    for post in subreddit.hot(limit=maxPosts):
        texte = post.title + ". " + post.selftext
        texte = texte.replace("\n", " ").replace("\r", " ")

        if len(texte) < 20:
            continue

        doc = Document(
            titre=post.title,
            auteur=str(post.author),
            date=post.created_utc,
            url=post.url,
            texte=texte
        )

        corpus.add_document(doc)

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
        if isinstance(authors, dict):
            author_names = [authors['name']]
        else:
            author_names = [a['name'] for a in authors]

        for auteur in author_names:
            doc = Document(
                titre=entry['title'],
                auteur=auteur,
                date=0,
                url=entry['id'],
                texte=texte
            )
            corpus.add_document(doc)

    return corpus

# -------------------------
# Programme principal
# -------------------------
def main():
    corpus = construire_corpus("jazz", 20)

    print(corpus)
    print("\nDocuments triés par date :")
    corpus.show_by_date(5)

    print("\nDocuments triés par titre :")
    corpus.show_by_title(5)

    # Sauvegarde
    corpus.save("corpus.csv")

    # Chargement
    corpus2 = Corpus.load("corpus.csv", "jazz_reloaded")
    print("\nCorpus rechargé :", corpus2)

    # Tests des classes filles :
    doc_reddit = RedditDocument(
        titre="Great jazz album",
        auteur="user123",
        date=1700000000,
        url="https://reddit.com/...",
        texte="This album is amazing",
        nb_comments=42
    )

    doc_arxiv = ArxivDocument(
        titre="Topology and Jazz",
        auteurs=["Octavio A. Agustín-Aquino", "Guerino Mazzola"],
        date=0,
        url="http://arxiv.org/abs/1234.5678",
        texte="This paper explores..."
    )

    print(doc_reddit)
    print(doc_arxiv)


if __name__ == "__main__":
    main()