from bs4 import BeautifulSoup
import email
import json 
import re
    
# https://stackoverflow.com/a/5707605/5917194
def _makeRegistrar():
    registry = {}
    def registrar(func):
        registry[func.__name__] = func
        return func  # normally a decorator returns a wrapped function, 
                     # but here we return func unmodified, after registering it
    registrar.all = registry
    return registrar



class ArticleParser():
    required_fields = [
        'headline', 
        # 'date_published', 
        # 'author', 
        'image_url', 
        'article_body']
    
    def __init__(self):
        self.create_registers()
    
    def parse(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        parsed = self._parse(soup)
        for required_field in self.required_fields:
            if required_field not in parsed:
                # pass
                raise Exception('parsed results did not include required field: `{}`'.format(required_field))
        return parsed
        
    def _parse(self, soup):
        parsed = {}
        for field in self.required_fields:
            _parsed_field = None
            for register_def in self.registers[field].all.values():
                if field == 'article_body':
                    # import pdb; pdb.set_trace()
                    pass
                try:
                    _parsed_field = register_def(soup)
                    if _parsed_field:
                        break
                except:
                    # import pdb; pdb.set_trace()
                    pass
            
            if not _parsed_field:
                raise Exception('Could not parse field: {}'.format(field))
                
            parsed[field] = _parsed_field
        
        return parsed
    
        
    def create_registers(self):
        self.registers = {}
        image_url_reg = _makeRegistrar()
        author_reg = _makeRegistrar()
        date_published_reg = _makeRegistrar()
        headline_reg = _makeRegistrar()
        article_body_reg = _makeRegistrar()
        
        self.registers['image_url'] = image_url_reg
        self.registers['author'] = author_reg
        self.registers['date_published'] = date_published_reg
        self.registers['headline'] = headline_reg
        self.registers['article_body'] = article_body_reg
        
        self._populate_registers(image_url_reg, 
            author_reg, 
            date_published_reg, 
            headline_reg, 
            article_body_reg)
        
    def _populate_registers(self, *args, **kwargs):
        raise Exception('not implemented!')
        
        
class WapoParser(ArticleParser):

    def _populate_registers(self, 
        image_url_reg, 
        author_reg, 
        date_published_reg, 
        headline_reg, 
        article_body_reg):
        
        @image_url_reg
        def get_image_url_2(soup):
            return soup.select_one('article figure img').attrs['src']
        
        @image_url_reg
        def get_image_url_3(soup):
            return soup.select_one('#end-screen-img').attrs['src']
        
        @image_url_reg
        def get_image_url_1(soup):
            return soup.select_one('.wp-volt-gal-embed-promo-mid-img-container img').attrs['src']
            
        @image_url_reg
        def get_image_url_4(soup):
            shot = soup.select_one('.powa-shot-image')
            # import pdb; pdb.set_trace()
            image_url = re.search("url\('(.+)'\)", shot.attrs['style']).group(1)
            return image_url
            
        @image_url_reg
        def get_image_url_5(soup):
            return soup.select_one('.inline-photo-center img').attrs['src']
        
        
        
        @author_reg
        def authors_1(soup):
            author_els = soup.select('[data-qa="byline"] .author-name')
            return ', '.join(list(set([author_name.string for author_name in author_els])))
            
        @author_reg
        def authors_2(soup):
            author_els = soup.select('[itemprop="author"]')
            return ', '.join(list(set([author.string for author in author_els])))
        
        @author_reg
        def authors_3(soup):
            return ', '.join(list(set([authorname.attrs['data-authorname'] for authorname in soup.select('[data-authorname]')])))

        
        @date_published_reg
        def date_published_1(soup):
            return soup.select_one('[data-qa="timestamp"] div').string
        
        @date_published_reg
        def date_published_2(soup):
            return soup.select_one('[itemprop="datePublished"]').string    
        

        
        @headline_reg
        def headline_1(soup):
            return soup.select_one('[data-qa="headline"]').string
        
        @headline_reg
        def headline_2(soup):
            return soup.select_one('[itemprop="headline"]').string
        

        
        @article_body_reg
        def article_body_1(soup):
            article_body = soup.select('.article_body p.font-copy')
            return str(article_body) if article_body else ''
        
        @article_body_reg
        def article_body_2(soup):
            article_body = soup.select('article p')
            return str(article_body) if article_body else ''
            
            

class FoxNewsParser(ArticleParser):

    def _populate_registers(self,
        image_url_reg, 
        author_reg, 
        date_published_reg, 
        headline_reg, 
        article_body_reg):
        
        @headline_reg
        def headline_1(soup):
            return soup.select_one('.headline').string
        
        @date_published_reg
        def date_p_1(soup):
            ld_json = json.loads(soup.select('script[type="application/ld+json"]')[0].string)
            return ld_json['datePublished']
            
        @date_published_reg
        def date_p_2(soup):
            return soup.select_one('.article-date time').string
        
        @author_reg
        def author_1(soup):
            ld_json = json.loads(soup.select('script[type="application/ld+json"]')[0].string)
            return ld_json['author']['name']
            
        @author_reg
        def author_2(soup):
            return soup.select_one('.author-byline span:not(.article-source) a').string
            
        @image_url_reg
        def image_url_1(soup):
            ld_json = json.loads(soup.select('script[type="application/ld+json"]')[0].string)
            return ld_json['image']['url']
        
        @image_url_reg
        def image_url_2(soup):
            return soup.select_one('meta[data-hid="og:image"]').attrs['content']
        
            
        @article_body_reg
        def article_body_1(soup):
            article_body = soup.select('.article-content p')
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
                try:
                    els = article_body.select(decompose_this)
                    for el in els:
                        el.decompose()
                except:
                    pass
            return str(article_body)
            
class NewYorkTimesParser(ArticleParser):
    
    def _populate_registers(self,
        image_url_reg, 
        author_reg, 
        date_published_reg, 
        headline_reg, 
        article_body_reg):
        
        @date_published_reg
        def dp_1(soup):
            return soup.select_one('meta[property="article:published"]').attrs['content']
        
        @image_url_reg
        def img_1(soup):
            return soup.select_one('meta[itemprop="image"]').attrs['content']
            
        @author_reg
        def byl_1(soup):
            return soup.select_one('meta[name="byl"]').attrs['content']
        
        @headline_reg
        def headline_1(soup):
            return soup.select_one('meta[property="og:title"]').attrs['content']
        
        @article_body_reg
        def article_body(soup):
            return str(soup.select('section[itemprop="articleBody"] p'))
        
class AssociatedPressParser(ArticleParser):
    def _populate_registers(self,
        image_url_reg, 
        author_reg, 
        date_published_reg, 
        headline_reg, 
        article_body_reg):
        
        @date_published_reg
        def dp_1(soup):
            # <meta data-rh="true" property="article:published_time" content="2019-11-01T21:50:58Z"> 
            return soup.select_one('meta[property="article:published_time"]').attrs['content']
        
        @image_url_reg
        def img_1(soup):
            # <meta data-rh="true" property="og:image" content="https://storage.googleapis.com/afs-prod/media/b91763af9125419f99c733a9eb887eab/3000.jpeg">
            return soup.select_one('meta[property="og:image"]').attrs['content']
            
        # @author_reg
        
        @headline_reg
        def headline_1(soup):
            # <meta data-rh="true" property="og:title" content="Warren vows no middle class tax hike for $20T health plan">
            return soup.select_one('meta[property="og:title"]').attrs['content']
        
        @article_body_reg
        def article_body(soup):
            # <div class="Article" data-key="article">
            return str(soup.select('[data-key="article"] p'))
            
class ReutersParser(ArticleParser):
    def _populate_registers(self,
        image_url_reg, 
        author_reg, 
        date_published_reg, 
        headline_reg, 
        article_body_reg):
        
        @headline_reg
        def headline_1(soup):
            # <meta data-rh="true" property="og:title" content="Warren vows no middle class tax hike for $20T health plan">
            return soup.select_one('meta[property="og:title"]').attrs['content']
            
        @date_published_reg
        def dp_1(soup):
            # <meta data-rh="true" property="article:published_time" content="2019-11-01T21:50:58Z"> 
            return soup.select_one('meta[property="og:article:published_time"]').attrs['content']
        
        @image_url_reg
        def img_1(soup):
            # <meta data-rh="true" property="og:image" content="https://storage.googleapis.com/afs-prod/media/b91763af9125419f99c733a9eb887eab/3000.jpeg">
            return soup.select_one('meta[property="og:image"]').attrs['content']
        
        @article_body_reg
        def article_body(soup):
            # <div class="Article" data-key="article">
            return str(soup.select('.StandardArticleBody_body p'))
            
class TheAtlanticParser(ArticleParser):
    def _populate_registers(self,
        image_url_reg, 
        author_reg, 
        date_published_reg, 
        headline_reg, 
        article_body_reg):
        
        @headline_reg
        def headline_1(soup):
            # <meta data-rh="true" property="og:title" content="Warren vows no middle class tax hike for $20T health plan">
            return soup.select_one('meta[property="og:title"]').attrs['content']
            
        @date_published_reg
        def dp_1(soup):
            # <meta data-rh="true" property="article:published_time" content="2019-11-01T21:50:58Z"> 
            return soup.select_one('meta[property="article:published_time"]').attrs['content']
        
        @image_url_reg
        def img_1(soup):
            # <meta data-rh="true" property="og:image" content="https://storage.googleapis.com/afs-prod/media/b91763af9125419f99c733a9eb887eab/3000.jpeg">
            return soup.select_one('meta[property="og:image"]').attrs['content']
        
        @article_body_reg
        def article_body(soup):
            # <section class="l-article__section s-cms-content" itemprop="articleBody" id="article-section-0">  
            return str(soup.select('section[itemprop="articleBody"] p'))
            
class WashingtonExaminerParser(ArticleParser):
    def _populate_registers(self,
        image_url_reg, 
        author_reg, 
        date_published_reg, 
        headline_reg, 
        article_body_reg):
        
        @headline_reg
        def headline_1(soup):
            # <meta data-rh="true" property="og:title" content="Warren vows no middle class tax hike for $20T health plan">
            return soup.select_one('meta[property="og:title"]').attrs['content']
            
        @date_published_reg
        def dp_1(soup):
            # <meta data-rh="true" property="article:published_time" content="2019-11-01T21:50:58Z"> 
            return soup.select_one('meta[property="article:published_time"]').attrs['content']
        
        @image_url_reg
        def img_1(soup):
            # <meta data-rh="true" property="og:image" content="https://storage.googleapis.com/afs-prod/media/b91763af9125419f99c733a9eb887eab/3000.jpeg">
            return soup.select_one('meta[property="og:image"]').attrs['content']
        
        @article_body_reg
        def article_body(soup):
            # <section class="l-article__section s-cms-content" itemprop="articleBody" id="article-section-0">  
            return str(soup.select('[itemprop="articleBody"] p'))

class WashingtonTimesParser(ArticleParser):
    def _populate_registers(self,
        image_url_reg, 
        author_reg, 
        date_published_reg, 
        headline_reg, 
        article_body_reg):
        
        @headline_reg
        def headline_1(soup):
            # <meta data-rh="true" property="og:title" content="Warren vows no middle class tax hike for $20T health plan">
            return soup.select_one('meta[property="og:title"]').attrs['content']
        
        @image_url_reg
        def img_1(soup):
            # <meta data-rh="true" property="og:image" content="https://storage.googleapis.com/afs-prod/media/b91763af9125419f99c733a9eb887eab/3000.jpeg">
            return soup.select_one('meta[property="og:image"]').attrs['content']
        
        @article_body_reg
        def article_body(soup):
            # <section class="l-article__section s-cms-content" itemprop="articleBody" id="article-section-0">  
            return str(soup.select('.storyareawrapper p'))
            
class YahooNewsParser(ArticleParser):
    def _populate_registers(self,
        image_url_reg, 
        author_reg, 
        date_published_reg, 
        headline_reg, 
        article_body_reg):
        
        @headline_reg
        def headline_1(soup):
            # <meta data-rh="true" property="og:title" content="Warren vows no middle class tax hike for $20T health plan">
            return soup.select_one('meta[property="og:title"]').attrs['content']
        
        @image_url_reg
        def img_1(soup):
            # <meta data-rh="true" property="og:image" content="https://storage.googleapis.com/afs-prod/media/b91763af9125419f99c733a9eb887eab/3000.jpeg">
            return soup.select_one('meta[property="og:image"]').attrs['content']
        
        @article_body_reg
        def article_body(soup):
            # <section class="l-article__section s-cms-content" itemprop="articleBody" id="article-section-0">  
            return str(soup.select('[itemprop="articleBody"] p'))

class TheHillParser(ArticleParser):
    def _populate_registers(self,
        image_url_reg, 
        author_reg, 
        date_published_reg, 
        headline_reg, 
        article_body_reg):
        
        @headline_reg
        def headline_1(soup):
            # <meta data-rh="true" property="og:title" content="Warren vows no middle class tax hike for $20T health plan">
            return soup.select_one('meta[property="og:title"]').attrs['content']
        
        @image_url_reg
        def img_1(soup):
            # <meta data-rh="true" property="og:image" content="https://storage.googleapis.com/afs-prod/media/b91763af9125419f99c733a9eb887eab/3000.jpeg">
            return soup.select_one('meta[property="og:image"]').attrs['content']
        
        @article_body_reg
        def article_body(soup):
            # <section class="l-article__section s-cms-content" itemprop="articleBody" id="article-section-0">  
            return str(soup.select('.content-wrp p'))


class ABCNewsParser(ArticleParser):
    def _populate_registers(self,
        image_url_reg, 
        author_reg, 
        date_published_reg, 
        headline_reg, 
        article_body_reg):
        
        @headline_reg
        def headline_1(soup):
            # <meta data-rh="true" property="og:title" content="Warren vows no middle class tax hike for $20T health plan">
            return soup.select_one('meta[property="og:title"]').attrs['content']
        
        @image_url_reg
        def img_1(soup):
            # <meta data-rh="true" property="og:image" content="https://storage.googleapis.com/afs-prod/media/b91763af9125419f99c733a9eb887eab/3000.jpeg">
            return soup.select_one('meta[property="og:image"]').attrs['content']
        
        @article_body_reg
        def article_body(soup):
            # <section class="l-article__section s-cms-content" itemprop="articleBody" id="article-section-0">  
            return str(soup.select('article p'))
 
parser_map = {
    'Washington Post': WapoParser(),
    'Fox Online News': FoxNewsParser(),
    'New York Times': NewYorkTimesParser(),
    'Associated Press': AssociatedPressParser(),
    'Reuters': ReutersParser(),
    'The Atlantic': TheAtlanticParser(),
    'Washington Examiner': WashingtonExaminerParser(),
    'Washington Times': WashingtonTimesParser(),
    'Yahoo! News': YahooNewsParser(),
    'The Hill': TheHillParser(),
    'ABC News': ABCNewsParser()
}