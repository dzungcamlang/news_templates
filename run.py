#!/home/deargle/.virtualenvs/fake-news/bin/python
import requests
from bs4 import BeautifulSoup
import json
import hashlib
from os import path
import sys
import gspread
from pymongo import MongoClient, ReturnDocument
client = MongoClient()

import pandas as pd

db = client.fake_news

#
# load values from google-sheet
#

refresh_articles = False
if refresh_articles or not path.exists('articles.csv'):
    from authenticate import authenticate 
    credentials = authenticate()
    gc = gspread.authorize(credentials)

    worksheet = gc.open_by_url('https://docs.google.com/spreadsheets/d/1EQJh_o8nOplUy0SKEpy-iSv123915sbZh5-JZCPXjds/edit#gid=0').get_worksheet(0)

    ws_values = worksheet.get_all_values()
    articles = pd.DataFrame.from_records(ws_values[1:], columns = ws_values[0])

    articles.to_csv('articles.csv')
else:
    articles = pd.read_csv('articles.csv')

#(Pdb) articles.columns
#Index(['Leaning', 'Source', 'Topic', 'Allsides', 'Article', 'md5'], dtype='object')
articles_with_url = articles[articles.ArticleUrl.notnull()]
wapo_articles = articles_with_url[articles.Source == 'Washington Post']
do_these = wapo_articles

from article_parsers import parser_map

for index, do_this in do_these.iterrows():
    url = do_this['ArticleUrl']
    url_hash = hashlib.md5(url.encode()).hexdigest()
    query = { '_id': url_hash }
    
    # update the mongo record with any changes from the google sheet
    db.pages.update_one(
        query,
        { '$set': do_this.to_dict() },
        upsert = True
    )
    
    # pull the mongo record and maybe update its html
    record = db.pages.find_one(query)
    
    if 'html' not in record:
        article_cache_path = 'article_pages/{}'.format(url_hash)
        if not path.exists(article_cache_path):
            pass
            # raise Exception('html for record {} not set and cached html not found in article_pages dir'.format(url_hash))
        else:
            with open(article_cache_path.format(url_hash, 'r')) as f:
                html = f.read()
            record = db.pages.find_one_and_update(
                query,
                { '$set': { 'html' : html } },
                return_document = ReturnDocument.AFTER
            )
    
    # parse, and update database record...
    # parsed_fields = parser_map[record['Source']].parse(record['html'])
    # db.pages.update_one(
        # query, 
        # { '$set': parsed_fields }
    # )
    
    