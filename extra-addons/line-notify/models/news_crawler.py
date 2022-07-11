from odoo import models, fields, api
from gnews import GNews
from newspaper import Article,Config
from datetime import datetime,timedelta
import requests, json, asyncio, time, urllib, newspaper, logging
from bs4 import BeautifulSoup
from requests_html import AsyncHTMLSession
_logger = logging.getLogger(__name__)

class News_crawler(models.Model):
    _name = 'news_crawler'
    _description = '根據關鍵字爬取 News'

    name = fields.Char('新聞標題')
    publisher = fields.Char('發布者')
    url = fields.Char('連結')
    date = fields.Datetime('發布時間')
    keyword = fields.Char('關鍵字')

    token = 'here'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36'
    }
    def line_notify(self,token, msg): #, picURI):
        url = "https://notify-api.line.me/api/notify"
        headers = {
            "Authorization": "Bearer " + token
        }
        payload = {'message': msg}
        r = requests.post(url, headers = headers, params = payload)#, files = files)
        return r.status_code
    def all_keywords(*keywords,type):
        all_words = ''
        if type == 'urlencode':
            for word in keywords[1:]:
                all_words += urllib.parse.quote(str(word)) + '%20'
            return all_words[0:-3]
        else:
            for word in keywords[1:]:
                all_words += str(word) + '&'
            return all_words[0:-1]
    def get_google_news(self,keyword,token=token):
        google_news = GNews(language='zh-Hant', country='TW', period='4h')
        news = google_news.get_news(keyword)
        news_count = len(news)
        config = Config()
        config.request_timeout = 10
        config.browser_user_agent = self.headers['user-agent']
        for i in range(news_count):
            title = news[i]['title'].split(' - ')[0].replace('\u3000',' ') #去除發布者 & 將全形space取代為半形space
            url = news[i]['url'].replace('https://m.ltn','https://news.ltn') #如果有m版網址，將其取代
            publisher = news[i]['publisher']['title']
            dateString = news[i]['published date']
            dateFormatter = "%a, %d %b %Y %H:%M:%S GMT"
            published_date = datetime.strptime(dateString, dateFormatter)
            expect_time = datetime.today() - timedelta(hours=1)
            article = Article(url,config=config)
            try:
                _logger.debug('===================================')
                _logger.debug(f'keyword: {keyword} publisher: {publisher} token: {token}')
                article.download()
                article.parse()
                if keyword in article.text and 'from' not in url and 'yahoo' not in url:
                    if len(self.search([("url","=",url)])) == 0  and len(self.search([("name","=",title)])) == 0:
                        if published_date >= expect_time:
                            create_record = self.create({
                                'id':1,
                                'name': title,
                                'publisher':publisher,
                                'url': url,
                                'date': published_date,
                                'keyword':keyword
                            })
                            self.env.cr.commit()
                            if create_record:
                                line_token = self.env['config_token'].search([('env_name','=',token)]).line_token
                                self.line_notify(line_token, title + " 〔" + keyword + "〕 " + url)   #發送 Line Notify 訊息
                        else:
                            break
                    else:
                        break
            except newspaper.article.ArticleException:
                continue
    async def get_udn_news(self,s,*keywords,token=token): 
        keyword_urlencode = self.all_keywords(*keywords,type='urlencode')
        keyword = self.all_keywords(*keywords,type='string')
        _logger.debug(*keywords)
        _logger.debug('get_udn_news')
        _logger.debug(keyword_urlencode)
        _logger.debug(keyword)
        udn_url = 'https://udn.com/api/more?page=0&id=search:'+ keyword_urlencode +'&channelId=2&type=searchword'            
        res = requests.get(url=udn_url,headers=self.headers)
        news = res.json()['lists']
        publisher = 'UDN聯合新聞網'
        for i in range(len(news)):
            url = news[i]['titleLink']
            title = news[i]['title'].replace('\u3000',' ') #將全形space取代為半形space
            dateString = news[i]['time']['date']
            dateFormatter = "%Y-%m-%d %H:%M:%S"
            published_date = datetime.strptime(dateString, dateFormatter)
            expect_time = datetime.today() - timedelta(hours=1)
            _logger.debug('===================================')
            _logger.debug(f'keyword: {keyword} publisher: {publisher} token: {token}')
            if 'from' not in url:
                if len(self.search([("url","=",url)])) == 0  and len(self.search([("name","=",title)])) == 0:
                    if published_date >= expect_time:
                        create_record = self.create({
                            'id':1,
                            'name': title,
                            'publisher': publisher,
                            'url': url,
                            'date': published_date - timedelta(hours=8),
                            'keyword':keyword
                        })
                        self.env.cr.commit()
                        if create_record:
                            line_token = self.env['config_token'].search([('env_name','=',token)]).line_token
                            self.line_notify(line_token, title + " 〔" + keyword + "〕 " + url)   #發送 Line Notify 訊息
                    else:
                        break
                else:
                    break
    async def get_apple_news(self,s,*keywords,token=token): 
        keyword_urlencode = self.all_keywords(*keywords,type='urlencode')
        keyword = self.all_keywords(*keywords,type='string')
        apply_url = 'https://tw.appledaily.com/search/' + urllib.parse.quote_plus(keyword_urlencode)
        res = requests.get(url=apply_url,headers=self.headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        publish = soup.select('div.timestamp')
        for i in range(len(publish)):
            title = soup.select('span.headline')[i].text
            dateString = soup.select('div.timestamp')[i].text
            dateFormatter = "出版時間：%Y/%m/%d %H:%M"
            published_date = datetime.strptime(dateString, dateFormatter)
            publisher = '蘋果新聞網'
            url = 'https://tw.appledaily.com/'+soup.select('a.story-card')[i].get('href')
            expect_time = datetime.today() - timedelta(hours=1)
            _logger.debug('===================================')
            _logger.debug(f'keyword: {keyword} publisher: {publisher} token: {token}')    
            if len(self.search([("url","=",url)])) == 0  and len(self.search([("name","=",title)])) == 0:
                if published_date >= expect_time:
                    create_record = self.create({
                        'id':1,
                        'name': title,
                        'publisher': publisher,
                        'url': url,
                        'date': published_date,
                        'keyword':keyword
                    })
                    self.env.cr.commit()
                    if create_record:
                        line_token = self.env['config_token'].search([('env_name','=',token)]).line_token
                        self.line_notify(line_token, title + " 〔" + keyword + "〕 " + url)   #發送 Line Notify 訊息
                else:
                    break
            else:
                break
    async def get_ltn_news(self,s,*keywords,token=token):
        keyword_urlencode = self.all_keywords(*keywords,type='urlencode')
        keyword = self.all_keywords(*keywords,type='string')
        url = 'https://search.ltn.com.tw/list?keyword=' + keyword_urlencode
        res = requests.get(url=url,headers=self.headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        titles = soup.find_all("a", class_="tit")
        publisher = '自由時報電子報'
        for i in range(len(titles)):
            title = titles[i]['title'].replace('\u3000',' ') #將全形space取代為半形space
            url = titles[i]['href']
            _logger.debug('===================================')
            _logger.debug(f'keyword: {keyword} publisher: {publisher} token: {token}')    
            try:
                res = requests.get(url=url,headers=self.headers, timeout = 10)
                soup = BeautifulSoup(res.text, 'html.parser')
                publish = soup.select('span.time')[0].text.replace('\n    ','').replace('\r','')
                if publish == "":
                    publish = soup.select('span.time')[1].text.replace('\n    ','').replace('\r','')
                if len(self.search([("url","=",url)])) == 0  and len(self.search([("name","=",title)])) == 0:
                    dateFormatter = "%Y/%m/%d %H:%M"
                    published_date = datetime.strptime(publish, dateFormatter)
                    expect_time = datetime.today() - timedelta(hours=1)
                    if published_date >= expect_time:
                        create_record = self.create({
                                'id':1,
                                'name': title,
                                'publisher': publisher,
                                'url':url,
                                'date': published_date - timedelta(hours=8),
                                'keyword':keyword
                        })
                        self.env.cr.commit()
                        if create_record:
                            line_token = self.env['config_token'].search([('env_name','=',token)]).line_token
                            self.line_notify(line_token, title + " 〔" + keyword + "〕 " + url)   #發送 Line Notify 訊息
                    else:
                        break
                else:
                    break
            except requests.exceptions.RequestException as e:  # This is the correct syntax:
                continue
    async def get_setn_news(self,s,*keywords,token=token):
        keyword_urlencode = self.all_keywords(*keywords,type='urlencode')
        keyword = self.all_keywords(*keywords,type='string')
        url = 'https://www.setn.com/search.aspx?q='+ keyword_urlencode +'&r=0'
        res = requests.get(url=url,headers=self.headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        titles = soup.select('div.newsimg-area-text-2')
        url_tag = soup.select("div.newsimg-area-info >  a.gt ")
        dates = soup.select('div.newsimg-date')
        publisher = '三立新聞網'
        for i in range(len(titles)):
            title = titles[i].text.replace('\u3000',' ') #將全形space取代為半形space
            dateString = dates[i].text
            url = 'https://www.setn.com/' + url_tag[i].get('href').replace('&From=Search','')
            dateFormatter = "%Y/%m/%d %H:%M"
            published_date = datetime.strptime(dateString, dateFormatter)
            expect_time = datetime.today() - timedelta(hours=1)
            _logger.debug('===================================')
            _logger.debug(f'keyword: {keyword} publisher: {publisher} token: {token}')    
            if len(self.search([("url","=",url)])) == 0  and len(self.search([("name","=",title)])) == 0:
                if published_date >= expect_time:
                    create_record = self.create({
                                'id':1,
                                'name': title,
                                'publisher': publisher,
                                'url':url,
                                'date': published_date - timedelta(hours=8),
                                'keyword':keyword
                    })
                    self.env.cr.commit()
                    if create_record:
                        line_token = self.env['config_token'].search([('env_name','=',token)]).line_token
                        self.line_notify(line_token, title + " 〔" + keyword + "〕 " + url)   #發送 Line Notify 訊息
                else:
                    break
            else:
                break
    async def get_ettoday_news(self,s,*keywords,token=token): 
        keyword_urlencode = self.all_keywords(*keywords,type='urlencode')
        keyword = self.all_keywords(*keywords,type='string')
        url = 'https://www.ettoday.net/news_search/doSearch.php?search_term_string='+ keyword_urlencode
        res = requests.get(url=url,headers=self.headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        titles = soup.select('h2 > a')
        date = soup.select('span.date')
        publisher = 'ETtoday新聞雲'
        for i in range(len(titles)):
            title = titles[i].text.replace('\u3000',' ') #將全形space取代為半形space
            url = titles[i].get('href')
            publish = date[i].text.split('/')[1].replace(' ','')
            dateFormatter = "%Y-%m-%d%H:%M)"
            published_date = datetime.strptime(publish, dateFormatter)
            _logger.debug('===================================')
            _logger.debug(f'keyword: {keyword} publisher: {publisher} token: {token}')    
            if len(self.search([("url","=",url)])) == 0  and len(self.search([("name","=",title)])) == 0:
                expect_time = datetime.today() - timedelta(hours=1)
                if published_date >= expect_time:
                    create_record = self.create({
                                'id':1,
                                'name': title,
                                'publisher': publisher,
                                'url':url,
                                'date': published_date - timedelta(hours=8),
                                'keyword':keyword
                    })
                    self.env.cr.commit()
                    if create_record:
                        line_token = self.env['config_token'].search([('env_name','=',token)]).line_token
                        self.line_notify(line_token, title + " 〔" + keyword + "〕 " + url)   #發送 Line Notify 訊息
                else:
                    break
            else:
                break
    async def get_TVBS_news(self,s,*keywords,token=token): 
        keyword_urlencode = self.all_keywords(*keywords,type='urlencode')
        keyword = self.all_keywords(*keywords,type='string')
        url = 'https://news.tvbs.com.tw/news/searchresult/'+ keyword_urlencode +'/news'
        res = requests.get(url=url,headers=self.headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        titles = soup.select('h2.search_list_txt')
        urls = soup.select('span.search_list_box > a')
        dates = soup.select('span.publish_date')
        publisher = 'TVBS新聞網'
        for i in range(len(titles)):
            title = titles[i].text.replace('\u3000',' ') #將全形space取代為半形space
            url = urls[i].get('href')
            publish = dates[i].text
            dateFormatter = "%Y/%m/%d %H:%M"
            published_date = datetime.strptime(publish, dateFormatter)
            _logger.debug('===================================')
            _logger.debug(f'keyword: {keyword} publisher: {publisher} token: {token}')    
            if len(self.search([("url","=",url)])) == 0  and len(self.search([("name","=",title)])) == 0:
                expect_time = datetime.today() - timedelta(hours=1)
                if published_date >= expect_time:
                    create_record = self.create({
                                'id':1,
                                'name': title,
                                'publisher': publisher,
                                'url':url,
                                'date': published_date - timedelta(hours=8),
                                'keyword':keyword
                    })
                    self.env.cr.commit()
                    if create_record:
                        line_token = self.env['config_token'].search([('env_name','=',token)]).line_token
                        self.line_notify(line_token, title + " 〔" + keyword + "〕 " + url)   #發送 Line Notify 訊息
                else:
                    break
            else:
                break
    async def get_china_news(self,s,*keywords,token=token):
        keyword_urlencode = self.all_keywords(*keywords,type='urlencode')
        keyword = self.all_keywords(*keywords,type='string')
        url = 'https://www.chinatimes.com/search/'+ keyword_urlencode +'?chdtv'
        res = requests.get(url=url,headers=self.headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        titles = soup.select('h3 > a')
        dates = soup.select('time')
        publisher = '中時新聞網'
        for i in range(len(titles)):
            title = titles[i].text.replace('\u3000',' ') #將全形space取代為半形space
            url = titles[i].get('href')
            dateString = dates[i].get('datetime')
            dateFormatter = "%Y-%m-%d %H:%M"
            published_date = datetime.strptime(dateString, dateFormatter)
            expect_time = datetime.today() - timedelta(hours=1)
            _logger.debug('===================================')
            _logger.debug(f'keyword: {keyword} publisher: {publisher} token: {token}')    
            if len(self.search([("url","=",url)])) == 0  and len(self.search([("name","=",title)])) == 0:
                if published_date >= expect_time:
                    create_record = self.create({
                            'id':1,
                            'name': title,
                            'publisher': publisher,
                            'url':url,
                            'date': published_date - timedelta(hours=8),
                            'keyword':keyword
                    })
                    self.env.cr.commit()
                    if create_record:
                        line_token = self.env['config_token'].search([('env_name','=',token)]).line_token
                        self.line_notify(line_token, title + " 〔" + keyword + "〕 " + url)   #發送 Line Notify 訊息
                else:
                    break
            else:
                break
    async def get_storm_news(self,s,*keywords,token=token): 
        keyword_urlencode = self.all_keywords(*keywords,type='urlencode')
        keyword = self.all_keywords(*keywords,type='string')
        url = 'https://www.storm.mg/site-search/result?q='+ keyword_urlencode +'&order=none&format=week'
        res = requests.get(url=url,headers=self.headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        titles = soup.select('p.card_title')
        urls = soup.select('a.card_substance')
        publish_dates = soup.select('span.info_time')
        publisher = '風傳媒'
        for i in range(len(titles)):
            title = titles[i].text.replace('\u3000',' ') #將全形space取代為半形space
            url = 'https://www.storm.mg' + urls[i].get('href').replace('?kw='+keyword+'&pi=0','')
            publish_date = publish_dates[i].text
            dateFormatter = "%Y-%m-%d %H:%M"
            published_date = datetime.strptime(publish_date, dateFormatter)
            expect_time = datetime.today() - timedelta(hours=1)
            _logger.debug('===================================')
            _logger.debug(f'keyword: {keyword} publisher: {publisher} token: {token}')    
            if len(self.search([("url","=",url)])) == 0  and len(self.search([("name","=",title)])) == 0:
                if published_date >= expect_time:
                    create_record = self.create({
                                        'id':1,
                                        'name': title,
                                        'publisher': publisher,
                                        'url':url,
                                        'date': published_date - timedelta(hours=8),
                                        'keyword':keyword
                                    })
                    self.env.cr.commit()
                    if create_record:
                        line_token = self.env['config_token'].search([('env_name','=',token)]).line_token
                        self.line_notify(line_token, title + " 〔" + keyword + "〕 " + url)   #發送 Line Notify 訊息
                else:
                    break
            else:
                break
    async def get_ttv_news(self,s,*keywords,token=token): 
        keyword_urlencode = self.all_keywords(*keywords,type='urlencode')
        keyword = self.all_keywords(*keywords,type='string')
        url = 'https://news.ttv.com.tw/search/' + keyword_urlencode
        res = requests.get(url=url,headers=self.headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        titles = soup.select('div.title')
        urls = soup.select('ul > li > a.clearfix')
        publishes = soup.select('div.time')
        publisher = '台視新聞網'
        for i in range(len(urls)):
            url = 'https://news.ttv.com.tw/'+urls[i].get('href')
            title = titles[i+2].text.replace('\u3000',' ') #將全形space取代為半形space
            publish = publishes[i].text
            dateFormatter = "%Y/%m/%d %H:%M:%S"
            published_date = datetime.strptime(publish, dateFormatter)
            expect_time = datetime.today() - timedelta(hours=1)
            _logger.debug('===================================')
            _logger.debug(f'keyword: {keyword} publisher: {publisher} token: {token}')    
            if len(self.search([("url","=",url)])) == 0  and len(self.search([("name","=",title)])) == 0:
                if published_date >= expect_time:
                    create_record = self.create({
                                        'id':1,
                                        'name': title,
                                        'publisher': publisher,
                                        'url':url,
                                        'date': published_date - timedelta(hours=8),
                                        'keyword':keyword
                                    })
                    self.env.cr.commit()
                    if create_record:
                        line_token = self.env['config_token'].search([('env_name','=',token)]).line_token
                        self.line_notify(line_token, title + " 〔" + keyword + "〕 " + url)   #發送 Line Notify 訊息
                else:
                    break
            else:
                break
    async def get_ftv_news(self,s,*keywords,token=token): 
        keyword_urlencode = self.all_keywords(*keywords,type='urlencode')
        keyword = self.all_keywords(*keywords,type='string')
        url = 'https://www.ftvnews.com.tw/search/' + keyword_urlencode
        res = requests.get(url=url,headers=self.headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        titles = soup.select('div.title')
        urls = soup.select('ul > li > a.clearfix')
        publishes = soup.select('div.time')
        publisher = '民視新聞網'
        for i in range(len(urls)):
            url = 'https://www.ftvnews.com.tw'+urls[i].get('href')
            title = titles[i].text.replace('\u3000',' ') #將全形space取代為半形space
            publish = publishes[i].text
            dateFormatter = "%Y/%m/%d %H:%M:%S"
            published_date = datetime.strptime(publish, dateFormatter)
            expect_time = datetime.today() - timedelta(hours=1)
            _logger.debug('===================================')
            _logger.debug(f'keyword: {keyword} publisher: {publisher} token: {token}')    
            if len(self.search([("url","=",url)])) == 0  and len(self.search([("name","=",title)])) == 0:
                if published_date >= expect_time:
                    create_record = self.create({
                                        'id':1,
                                        'name': title,
                                        'publisher': publisher,
                                        'url':url,
                                        'date': published_date - timedelta(hours=8),
                                        'keyword':keyword
                                    })
                    self.env.cr.commit()
                    if create_record:
                        line_token = self.env['config_token'].search([('env_name','=',token)]).line_token
                        self.line_notify(line_token, title + " 〔" + keyword + "〕 " + url)   #發送 Line Notify 訊息
                else:
                    break
            else:
                break
    async def get_cna_news(self,s,*keywords,token=token): 
        keyword_urlencode = self.all_keywords(*keywords,type='urlencode')
        keyword = self.all_keywords(*keywords,type='string')
        url = 'https://www.cna.com.tw/search/hysearchws.aspx?q=' + keyword_urlencode
        res = requests.get(url=url,headers=self.headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        urls = soup.select('ul.mainList > li > a')
        titles = soup.select('div.listInfo > h2')
        dates = soup.select('div.date')
        publisher = 'CNA中央社'
        for i in range(len(urls)):
            url = urls[i].get('href')
            title = titles[i].text.replace('\u3000',' ') #將全形space取代為半形space
            publish = dates[i].text
            dateFormatter = "%Y/%m/%d %H:%M"
            published_date = datetime.strptime(publish, dateFormatter)
            expect_time = datetime.today() - timedelta(hours=1)
            _logger.debug('===================================')
            _logger.debug(f'keyword: {keyword} publisher: {publisher} token: {token}')    
            if len(self.search([("url","=",url)])) == 0  and len(self.search([("name","=",title)])) == 0:
                if published_date >= expect_time:
                    create_record = self.create({
                                        'id':1,
                                        'name': title,
                                        'publisher': publisher,
                                        'url':url,
                                        'date': published_date - timedelta(hours=8),
                                        'keyword':keyword
                                    })
                    self.env.cr.commit()
                    if create_record:
                        line_token = self.env['config_token'].search([('env_name','=',token)]).line_token
                        self.line_notify(line_token, title + " 〔" + keyword + "〕 " + url)   #發送 Line Notify 訊息
                else:
                    break
            else:
                break
    async def main(self,*keywords,token=token):
        s = AsyncHTMLSession()
        udn_task = self.get_udn_news(s,*keywords,token=token)
        apple_task = self.get_apple_news(s,*keywords,token=token)
        setn_task = self.get_setn_news(s,*keywords,token=token)
        ettoday_task = self.get_ettoday_news(s,*keywords,token=token)
        tvbs_task = self.get_TVBS_news(s,*keywords,token=token)
        china_task = self.get_china_news(s,*keywords,token=token)
        storm_task = self.get_storm_news(s,*keywords,token=token)
        ttv_task = self.get_ttv_news(s,*keywords,token=token)
        ftv_task = self.get_ftv_news(s,*keywords,token=token)
        ltn_task = self.get_ltn_news(s,*keywords,token=token)
        cna_task = self.get_cna_news(s,*keywords,token=token)
        return await asyncio.gather(udn_task,apple_task,setn_task,ettoday_task,tvbs_task,china_task,storm_task,ttv_task,ftv_task,ltn_task,cna_task)
    def run_main(self,*keywords,token=token):
        asyncio.run(self.main(*keywords,token=token))
