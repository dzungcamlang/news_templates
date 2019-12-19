from flask import Flask, render_template, Markup
from flask_pymongo import PyMongo
from settings import APP_ROOT, APP_ARTICLES_CACHE
import os

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/fake_news'
mongo = PyMongo(app)

@app.route('/')
def index():
    foxnews_pages = list(mongo.db.pages.find({'news_source':'foxnews'}))
    cached_page_files = [file.casefold() for file in os.listdir(APP_ARTICLES_CACHE)]
    all_articles = mongo.db.pages.find()
    cached_articles = [article for article in all_articles if article['md5'].casefold() in cached_page_files]
    return render_template('index.html', fox_pages=foxnews_pages, cached_articles = cached_articles)
    
@app.route('/fox')
@app.route('/fox/<headline>')
def fox(headline=None):
    article_body = '<p>Yo.</p><p>Yo.</p><p>Yo.</p><p>Yo.</p><p>Yo.</p><p>Yo.</p><p>Yo.</p>'
    if headline:
        article = mongo.db.pages.find_one({'headline':headline})
        headline = article['headline']
        article_body = article['article_body']
    headline = 'a very nice headline'
    return render_template('fox.html', headline=headline, article_body=Markup(article_body))
    
@app.route('/cached/<hash>')
def cached(hash):
    with open(os.path.join(APP_ARTICLES_CACHE, hash.lower()), 'r') as f:
        html = f.read()
    return html