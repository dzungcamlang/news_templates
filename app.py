from flask import Flask, render_template, Markup
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/fake_news'
mongo = PyMongo(app)

@app.route('/')
def index():
    foxnews_pages = list(mongo.db.pages.find({'news_source':'foxnews'}))
    return render_template('index.html', fox_pages=foxnews_pages)
    
@app.route('/fox')
@app.route('/fox/<headline>')
def fox(headline=None):
    article_body = '<p>Yo.</p>'
    if headline:
        article = mongo.db.pages.find_one({'headline':headline})
        headline = article['headline']
        article_body = article['article_body']
    return render_template('fox.html', headline=headline, article_body=Markup(article_body))