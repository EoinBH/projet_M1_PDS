import pandas as pd
import praw
from praw.models import MoreComments
import urllib, urllib.request
#from xml.etree import cElementTree as ET
import xmltodict
import certifi
import ssl
#import pprint

theme = 'jazz'
docs = []

reddit = praw.Reddit(
    client_id='IDNxqb2cDUV0GxAlAUjplA',
    client_secret='A6Ar2mi-4xNnhSmTNRaxSSosngWIig',
    user_agent='InfoApp')

# EXAMPLE: Printing hot posts
# get hottest posts from all subreddits
#hot_posts = reddit.subreddit('all').hot(limit=10)
#for post in hot_posts:
    #print(post.title)

# EXAMPLE: Loading subreddit data
# get Machine Learning subreddit data
#ml_subreddit = reddit.subreddit('Machine Learning')

# EXAMPLE: Printing top comments from submission
#submission = reddit.submission(url="https://www.reddit.com/r/Jazz/comments/1nzc2qn/the_essential_miles_davis/")
#for top_level_comment in submission.comments:
    #if isinstance(top_level_comment, MoreComments):
        #continue
    #print(top_level_comment.body)

# Extraction of REDDIT DATA
posts = []
# get Jazz subreddit data
jz_subreddit = reddit.subreddit('Jazz')
numPosts_Reddit = 0
for post in jz_subreddit.hot(limit=100):
    posts.append([post.title, post.score, post.id, post.subreddit, post.url, post.num_comments, post.selftext, post.created])
    currTexte = post.title + ". " + post.selftext
    currTexte = currTexte.replace("\n", " ")
    currTexte = currTexte.replace("\r", " ")
    if (len(currTexte) >= 20):
        docs.append(currTexte)
    numPosts_Reddit += 1
posts = pd.DataFrame(posts,columns=['title', 'score', 'id', 'subreddit', 'url', 'num_comments', 'body', 'created'])
#print("\nprint posts:\n")
#print(posts)
#print(posts.at[0, 'body'])

#TRIAL AND ERROR
#textes_Arxiv = []
#query = "jazz"
#url = f'http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results=300'
#url_read = urllib.request.urlopen(url).read()
#data = url_read.decode()

#url = f'http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results=10'
#data = urllib.request.urlopen(url)
#print("\nprint arxiv data:\n")
#print(data.read().decode('utf-8'))
#xmlstr = data.read().decode('utf-8')
#print("\nXML STR:\n")
#print(xmlstr)
#my_ordered_dict = xmltodict.parse(xmlstr)
#for element in my_ordered_dict['summary']:
#    docs.append(element)

#xmlstr = data.read().decode('utf-8')
#root = ET.fromstring(xmlstr)
#for post in list(root):
#    summary = post.find('summary').text
#    docs.append(summary)
#for element in docs:
#    print(element)

# context = ssl.create_default_context(cafile=certifi.where())
# dataz = urllib.request.urlopen(url,context=context)
# libraires: certifi et ssl

# import certifi
# print(certifi.where())
# import ssl
# print(ssl.get_default_verify_paths())

#print("\nprint(certifi.where()):\n")
#print(certifi.where())
#print("\nprint(ssl.get_default_verify_paths()):\n")
#print(ssl.get_default_verify_paths())

# Extraction of ARXIV DATA
query = "jazz"
url = f'http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results=100'
context = ssl.create_default_context(cafile = certifi.where())
response = urllib.request.urlopen(url, context = context)
textes_Arxiv = xmltodict.parse(response.read())
numPosts_Arxiv = 0
for element in textes_Arxiv['feed']['entry']:
    currTexte = element['title'] + ". " + element['summary']
    currTexte = currTexte.replace("\n", " ")
    currTexte = currTexte.replace("\r", " ")
    if (len(currTexte) >= 20):
        docs.append(currTexte)
    numPosts_Arxiv += 1
#print(textes_Arxiv['feed']['entry'])
#pprint.pprint(textes_Arxiv, sort_dicts = False)
#df = pd.DataFrame([textes_Arxiv])
#print(df.columns)

#for entry in docs:
    #rint(entry + '\n\n')

# DataFrame Creation:
columns = {'id': [], 'text': [], 'source': []}
df = pd.DataFrame(data = columns)
for i in range(0, len(docs)):
    if (i < numPosts_Reddit):
        df.loc[i] = [i, docs[i], 'Reddit']
    else:
        df.loc[i] = [i, docs[i], 'Arxiv']

#print(df)
df.to_csv('output.csv', index = False)

def numDocuments():
    return len(df)

def numWords():
    words = 0
    for element in df['text']:
        words += len(element.split(" "))
    return words

def numSentences():
    sentences = 0
    for element in df['text']:
        sentences += len(element.split(". "))
    return sentences

def allContent():
    str = ""
    str = str.join(df['text'])
    return str

print(f"Num Documents = {numDocuments()}")
print(f"Num Words = {numWords()}")
print(f"Num Sentences = {numSentences()}")
print(f"All Content: {allContent()}")