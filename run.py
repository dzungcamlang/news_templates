#!/home/deargle/.virtualenvs/fake-news/bin/python
import requests
from bs4 import BeautifulSoup
import json
from pymongo import MongoClient
client = MongoClient()

db = client.fake_news
db.pages.create_index('headline')

foxnews_articles = [
    'https://www.foxnews.com/politics/mccarthy-brands-schiff-a-liar-pelosi-accuses-trump-of-bribery-as-impeachment-war-heats-up#'
]

for url in foxnews_articles:
    
    page = db.pages.find_one({'_id': url}, {'html': 1})
    if page:
        page = page['html']
    else:
        page = requests.get(url).text
        db.pages.insert_one({
            '_id': url,
            'html': page
        })
    soup = BeautifulSoup(page, 'html.parser')
    # import pdb; pdb.set_trace()
    
    record = {}
    record['news_source'] = 'foxnews'
    record['html'] = page
    record['headline'] = soup.select_one('.headline').string
    ld_json = json.loads(soup.select('script[type="application/ld+json"]')[0].string)
    record['date_published'] = ld_json['datePublished']
    record['author'] = ld_json['author']['name']
    record['publisher'] = ld_json['publisher']['name']
    record['image_url'] = ld_json['image']['url']
    
    article_body = soup.select_one('.article-content')
    decompose_these = [
        '#commenting', 
        '.featured-video', 
        '.article-source',
        '.sidebar',
        '.article-footer',
        '.article-meta',
        '.ad-container',
        '.ad']
    for decompose_this in decompose_these:
        for el in article_body.select(decompose_this):
            el.decompose()
    record['article_body'] = str(article_body)
    
    db.pages.replace_one({'_id': url}, record)
    
    
    
    
    
    

