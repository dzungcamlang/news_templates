from bs4 import BeautifulSoup
import json 



class ArticleParser():
    def __init__(self):
        self.required_fields = ['headline', 'date_published', 'author', 'publisher','image_url', 'article_body']
    
    def parse(self, html):
        parsed = self._parse(html)
        for required_field in self.required_fields:
            if required_field not in parsed:
                raise Exception('parsed results did not include required field {}'.format(required_field))
        return parsed
        
    def _parse(self, html):
        raise Exception('not implemented!')
        
class WapoParser(ArticleParser):
    def _parse(self, html):
        raise Exception('not implemented!')

class FoxNewsParser(ArticleParser):
    def _parse(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        record = {}
        record['news_source'] = 'foxnews'
        
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
        return record
 
wapo_parser = WapoParser()
foxnews_parser = FoxNewsParser()

parser_map = {
    'Washington Post': wapo_parser,
    'Fox Online News': foxnews_parser
}