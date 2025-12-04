import pandas as pd
import praw
from praw.models import MoreComments
import urllib, urllib.request
import xmltodict
import certifi
import ssl
from pathlib import Path

theme = 'jazz'
docs = []

reddit = praw.Reddit(
    client_id='IDNxqb2cDUV0GxAlAUjplA',
    client_secret='A6Ar2mi-4xNnhSmTNRaxSSosngWIig',
    user_agent='InfoApp')

def recupererDonnees(theme, maxPosts) :
    # Récupération des données de REDDIT :
    posts = []
    # On obtient les données du subreddit associé au thème :
    subreddit = reddit.subreddit(theme) # Thème : 'Jazz'
    numPosts_Reddit = 0
    for post in subreddit.hot(limit = maxPosts):
        posts.append([post.title, post.score, post.id, post.subreddit, post.url, post.num_comments, post.selftext, post.created])
        currTexte = post.title + ". " + post.selftext
        # On enlève les caractères de nouvelle ligne :
        currTexte = currTexte.replace("\n", " ")
        currTexte = currTexte.replace("\r", " ")
        # Vérification de la taille du texte :
        if (len(currTexte) >= 20):
            docs.append(currTexte)
        numPosts_Reddit += 1
    # Stocker toutes les informations dans un DataFrame :
    # [Pour l'instant on ne l'utilise pas]
    posts = pd.DataFrame(posts,columns=['title', 'score', 'id', 'subreddit', 'url', 'num_comments', 'body', 'created'])

    # Récupération des données de ARXIV :
    url = f'http://export.arxiv.org/api/query?search_query=all:{theme}&start=0&max_results={maxPosts}'
    context = ssl.create_default_context(cafile = certifi.where())
    response = urllib.request.urlopen(url, context = context)
    textes_Arxiv = xmltodict.parse(response.read())
    numPosts_Arxiv = 0
    for element in textes_Arxiv['feed']['entry']:
        currTexte = element['title'] + ". " + element['summary']
        # On enlève les caractères de nouvelle ligne :
        currTexte = currTexte.replace("\n", " ")
        currTexte = currTexte.replace("\r", " ")
        # Vérification de la taille du texte :
        if (len(currTexte) >= 20):
            docs.append(currTexte)
        numPosts_Arxiv += 1

    # Création du DataFrame
    columns = {'id': [], 'text': [], 'source': []}
    df = pd.DataFrame(data = columns)
    for i in range(0, len(docs)):
        if (i < numPosts_Reddit):
            df.loc[i] = [i, docs[i], 'Reddit']
        else:
            df.loc[i] = [i, docs[i], 'Arxiv']

    # Création du fichier csv
    df.to_csv('output.csv', index = False)

def readCSV():
    chemin = Path("./output.csv")
    if (chemin.exists()) :
        return pd.read_csv('output.csv')
    else :
        print("Fichier non trouvé, il faut de nouveau générer les données.")
        return None

def numDocuments(df):
    return len(df)

def numWords(df):
    words = 0
    for element in df['text']:
        words += len(element.split(" "))
    return words

def numSentences(df):
    sentences = 0
    for element in df['text']:
        sentences += len(element.split(". "))
    return sentences

def allContent(df):
    str = ""
    str = str.join(df['text'])
    return str

def main () :
    # Pour interroger les API si besoin :
    recupererDonnees(theme, 100)
    # Si les données ont déjà été récupérer :
    df = readCSV()
    if (df is None) :
        print("Données non chargées")
    else :
        print("Données chargées")

    print(f"Num Documents = {numDocuments(df)}")
    print(f"Num Words = {numWords(df)}")
    print(f"Num Sentences = {numSentences(df)}")
    print(f"All Content: {allContent(df)}")

main()