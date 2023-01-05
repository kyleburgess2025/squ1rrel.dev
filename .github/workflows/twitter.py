import tweepy
import requests
import xml.etree.ElementTree as ET
import os
from dotenv import load_dotenv
load_dotenv()

client = tweepy.Client(
    consumer_key=os.getenv("API_KEY"),
    consumer_secret=os.getenv("SECRET_KEY"),
    access_token=os.getenv("ACCESS_TOKEN"),
    access_token_secret=os.getenv("ACCESS_SECRET")
)

previous_atom = requests.get("https://squ1rrel.dev/atom.xml", allow_redirects=True).text
previous_tree = ET.fromstring(previous_atom)[0].findall('item')
current_tree = ET.parse('_site/atom.xml').getroot()[0].findall('item')
previous_title = previous_tree[0].find('title').text
print(previous_tree)
current_title = current_tree[0].find('title').text

i = 0
new_articles = []

while previous_title != current_title:
    print("Different!")
    new_articles.append(f'https://squ1rrel.dev{current_tree[i].find("link").text.strip()}')
    i += 1
    current_title = current_tree[i].find('title').text

if len(new_articles) > 0:
    if len(new_articles) == 1:
        tweet_text = f'New writeup!\n{new_articles[0]}'
    else:
        tweet_text = "New writeups!"
        for i in new_articles:
            tweet_text += "\n" + i
    if len(tweet_text) > 280:
        tweet_text = "New writeups at https://squ1rrel.dev!"
    client.create_tweet(text=tweet_text)
