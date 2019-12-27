#!/home/deargle/.virtualenvs/fake-news/bin/python
import requests
from bs4 import BeautifulSoup
import email
import json
import hashlib
import os
import sys
import gspread
from settings import APP_ARTICLES_CACHE 
from pymongo import MongoClient, ReturnDocument
client = MongoClient()

import pandas as pd

db = client.fake_news

#
# load values from google-sheet
#

refresh_articles = True
if refresh_articles or not os.path.exists('articles.csv'):
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
# wapo_articles = articles_with_url[articles.Source == 'Washington Post']
these_sources = [ 
    # 'Washington Post', 
    # 'Fox Online News',
    # 'New York Times',
    'Washington Examiner',
    'The Hill',
    'HuffPost',
    ]
    
these_topics = [
    '5. Healthcare'
]

# do_these = articles_with_url[articles_with_url['Source'].isin(these_sources)]
do_these = articles_with_url[articles_with_url['Topic'].isin(these_topics)]
# import pdb; pdb.set_trace()

from article_parsers import parser_map

for index, do_this in do_these.iterrows():
    url = do_this['ArticleUrl']
    url_hash = hashlib.md5(url.encode()).hexdigest().upper()
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
        article_cache_filepath = os.path.join(APP_ARTICLES_CACHE, '{}.mhtml'.format(url_hash))
        if not os.path.exists(article_cache_filepath):
            print('no cached article found, skipping, for {} {}'.format(article_cache_filepath, url))
            continue
            # raise Exception('html for record {} not set and cached html not found in article_pages dir'.format(url_hash))
        else:
            with open(article_cache_filepath, 'r') as f:
                message = email.message_from_file(f)
            html_parts = [ part for part in message.walk() if part.get_content_type() == 'text/html' ]
            html = html_parts[0].get_payload(decode=True)
            record = db.pages.find_one_and_update(
                query,
                { '$set': { 'html' : html } },
                return_document = ReturnDocument.AFTER
            )
    
    # parse, and update database record...
    try:
        parsed_fields = parser_map[record['Source']].parse(record['html'])
        parsed_fields.update({'parsed': True})
        db.pages.update_one(
            query, 
            { '$set': parsed_fields }
        )
    except Exception as e:
        print('exception hit while parsing {} {}'.format(url, url_hash))
        raise e
    
    
    