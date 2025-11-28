import pandas as pd
import praw
from praw.models import MoreComments
import urllib, urllib.request
import xmltodict
import certifi
import ssl

theme = 'jazz'
docs = []

reddit = praw.Reddit(
    client_id='IDNxqb2cDUV0GxAlAUjplA',
    client_secret='A6Ar2mi-4xNnhSmTNRaxSSosngWIig',
    user_agent='InfoApp')

# Extraction of REDDIT DATA
posts = []
# get Jazz subreddit data
jz_subreddit = reddit.subreddit('Jazz')
for post in jz_subreddit.hot(limit=10):
    posts.append([post.title, post.score, post.id, post.subreddit, post.url, post.num_comments, post.selftext, post.created])
    docs.append(post.selftext.replace('\n', ' '))
posts = pd.DataFrame(posts,columns=['title', 'score', 'id', 'subreddit', 'url', 'num_comments', 'body', 'created'])

# Extraction of ARXIV DATA
query = "jazz"
url = f'http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results=1'
context = ssl.create_default_context(cafile = certifi.where())
response = urllib.request.urlopen(url, context = context)
textes_Arxiv = xmltodict.parse(response.read())
for element in textes_Arxiv:
    currTexte = textes_Arxiv['feed']['entry']['summary'].replace('\n', ' ')
    docs.append(currTexte)

for entry in docs:
    print(entry + '\n\n')

# DataFrame Creation:
columns = {'id': [], 'text': [], 'source': []}
df = pd.DataFrame(data = columns)