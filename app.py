from flask import Flask, render_template, Markup, Response, send_file, make_response
from flask_pymongo import PyMongo
from settings import APP_ROOT, APP_ARTICLES_CACHE
from article_parsers import ArticleParser
import os
import email
from itertools import groupby

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/fake_news'
mongo = PyMongo(app)

def get_cached_articles():
    cached_page_files = [file.casefold() for file in os.listdir(APP_ARTICLES_CACHE)]
    all_articles = list(mongo.db.pages.find())
    
    cached_articles = [article for article in all_articles if '{}.mhtml'.format(article['md5'].casefold()) in cached_page_files]
    return cached_articles

@app.route('/')
@app.route('/groupby/<groupby>')
def index(groupby='source'):
    cached_articles = get_cached_articles()
    
    required_fields = ArticleParser.required_fields
    
    return render_template('index_by_{}.html'.format(groupby), 
        cached_articles = cached_articles, 
        required_fields = required_fields, 
        )
    
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
    response = make_response(send_file(os.path.join(APP_ARTICLES_CACHE, '{}.mhtml'.format(hash.upper())), as_attachment=True, mimetype='multipart/related'))
    # response.headers['Content-Disposition'] = 'inline'
    return response
    
    # import pdb; pdb.set_trace()
    # return str(message)
    # htmls = [part for part in message.walk() if part.get_content_type() == 'text/html']
    # return htmls[0].get_payload(decode=True)
    # stuff = MimeHtmlParser.parse_file(os.path.join(APP_ARTICLES_CACHE, hash.upper()))
    # return stuff.parts[0].content