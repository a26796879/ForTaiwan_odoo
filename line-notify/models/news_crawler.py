from odoo import models, fields, api
from gnews import GNews
from newspaper import Article
from datetime import datetime,timedelta
import requests, json
from bs4 import BeautifulSoup

class news_crawler(models.Model):
    _name = 'news_crawler'
    _description = '根據關鍵字爬取 Google News'

    name = fields.Char('新聞標題')
    publisher = fields.Char('發布者')
    url = fields.Char('連結')
    date = fields.Datetime('發布時間')

    def lineNotify(self,token, msg): #, picURI):
        url = "https://notify-api.line.me/api/notify"
        headers = {
            "Authorization": "Bearer " + token
        }
        payload = {'message': msg}
        r = requests.post(url, headers = headers, params = payload)#, files = files)
        return r.status_code

    def get_google_news(self,keyword):
        google_news = GNews(language='zh-Hant', country='TW', period='4h')
        news = google_news.get_news(keyword)
        news_count = len(news)
        # title,publisher,url,published date
        for i in range(news_count):
            article = Article(news[i]['url'])
            article.download()
            article.parse()
            title = news[i]['title']
            url = news[i]['url']
            publisher = news[i]['publisher']['title']
            if keyword in article.text and 'from' not in url:
                if 'yahoo' not in news[i]['url']:
                    if len(self.env['news_crawler'].search([("url","=",url)])) == 0  and len(self.env['news_crawler'].search([("name","=",title)])) == 0:
                        dateString = news[i]['published date']
                        dateFormatter = "%a, %d %b %Y %H:%M:%S GMT"
                        published_date = datetime.strptime(dateString, dateFormatter)
                        expect_time = datetime.today() - timedelta(hours=4)
                        if published_date >= expect_time:
                            create_record = self.create({
                                'id':1,
                                'name': title,
                                'publisher':publisher ,
                                'url': url,
                                'date': published_date
                            })
                            self.env.cr.commit()
                            if create_record:
                                #發送 Line Notify 訊息
                                token = self.env['config_token'].search([('env_name','=','here')]).line_token  # MySelf
                                self.lineNotify(token, title + " " + url)
    def get_udn_news(self,keyword): # not Article
        udn_url = 'https://udn.com/api/more?page=0&id=search:%E5%9F%BA%E9%80%B2&channelId=2&type=searchword'
        # 中時Ｘ TVBSＸ 自由時報Ｘ 三立Ｘ
        headers = {
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-TW,zh;q=0.9',
            'if-none-match': 'W/"989a-QvaRHTovk4mLrItkm2o2tDX3w/4"',
            'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
            'sec-ch-ua-mobile': '?0',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'
        }
        res = requests.get(url=udn_url,headers=headers)
        news = res.json()['lists']
        for i in range(len(news)):
            url = news[i]['titleLink']
            title = news[i]['title']
            if 'from' not in url:
                if len(self.env['news_crawler'].search([("url","=",url)])) == 0  and len(self.env['news_crawler'].search([("name","=",title)])) == 0:
                    dateString = news[i]['time']['date']
                    dateFormatter = "%Y-%m-%d %H:%M:%S"
                    published_date = datetime.strptime(dateString, dateFormatter)
                    expect_time = datetime.today() - timedelta(hours=1)
                    if published_date >= expect_time:
                        create_record = self.create({
                            'id':1,
                            'name': title,
                            'publisher': 'udn聯合新聞網',
                            'url': url,
                            'date': published_date - timedelta(hours=8)
                        })
                        self.env.cr.commit()
                        if create_record:
                            #發送 Line Notify 訊息
                            token = self.env['config_token'].search([('env_name','=','here')]).line_token  # MySelf
                            self.lineNotify(token, title + " " + url)
    def get_apple_news(self,keyword): # not Article
        apple_url = 'https://tw.appledaily.com/pf/api/v3/content/fetch/search-query?query=%7B%22searchTerm%22%3A%22%25E5%259F%25BA%25E9%2580%25B2%22%2C%22start%22%3A0%7D&d=264&_website=tw-appledaily'
        # 中時Ｘ TVBSＸ 自由時報Ｘ 三立Ｘ
        headers = {
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-TW,zh;q=0.9',
            'if-none-match': 'W/"989a-QvaRHTovk4mLrItkm2o2tDX3w/4"',
            'referer': 'https://tw.appledaily.com/search/%E5%9F%BA%E9%80%B2/',
            'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
            'sec-ch-ua-mobile': '?0',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'
        }
        res = requests.get(url=apple_url,headers=headers)
        news = res.json()['content']
        for i in range(len(news)):
            url = news[i]['sharing']['url']
            title = news[i]['title']
            if len(self.env['news_crawler'].search([("url","=",url)])) == 0  and len(self.env['news_crawler'].search([("name","=",title)])) == 0:
                dateString = news[i]['pubDate']
                published_date = datetime.fromtimestamp(int(dateString))
                expect_time = datetime.today() - timedelta(hours=1)
                if published_date >= expect_time:
                    create_record = self.create({
                        'id':1,
                        'name': title,
                        'publisher': news[i]['brandName'],
                        'url': url,
                        'date': published_date - timedelta(hours=8)
                    })
                    self.env.cr.commit()
                    if create_record:
                        #發送 Line Notify 訊息
                        token = self.env['config_token'].search([('env_name','=','here')]).line_token  # MySelf
                        self.lineNotify(token, title + " " + url)
    def get_ltn_news(self,keyword):
        url = 'https://search.ltn.com.tw/list?keyword=%E5%9F%BA%E9%80%B2'
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'referer': 'https://search.ltn.com.tw/list?keyword=%E5%9F%BA%E9%80%B2',
            'sec-ch-ua': '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36'
        }
        res = requests.get(url=url,headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        tit_tag = soup.find_all("a", class_="tit")
        for i in range(len(tit_tag)):
            title = tit_tag[i]['title']
            url = tit_tag[i]['href']
            article = Article(url)
            article.download()
            article.parse()
            if len(self.env['news_crawler'].search([("url","=",url)])) == 0  and len(self.env['news_crawler'].search([("name","=",title)])) == 0:
                dateString = article.publish_date.strftime("%Y-%m-%d %H:%M:%S")
                dateFormatter = "%Y-%m-%d %H:%M:%S"
                published_date = datetime.strptime(dateString, dateFormatter)
                expect_time = datetime.today() - timedelta(hours=1)
                if published_date >= expect_time:
                    create_record = self.create({
                            'id':1,
                            'name': title,
                            'publisher': '自由時報電子報',
                            'url':url,
                            'date': published_date - timedelta(hours=8)
                    })
                    self.env.cr.commit()
                    if create_record:
                        #發送 Line Notify 訊息
                        token = self.env['config_token'].search([('env_name','=','here')]).line_token  # MySelf
                        self.lineNotify(token, title + " " + url)
    def get_setn_news(self,keyword):# not Article
        url = 'https://www.setn.com/search.aspx?q=%E5%9F%BA%E9%80%B2&r=0'
        headers = {
            'authority': 'www.setn.com',
            'method': 'GET',
            'path': '/search.aspx?q=%E5%9F%BA%E9%80%B2',
            'scheme': 'https',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'sec-ch-ua': '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36'
        }
        res = requests.get(url=url,headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        titles = soup.select('div.newsimg-area-text-2')
        url_tag = soup.select("div.newsimg-area-info >  a.gt ")
        dates = soup.select('div.newsimg-date')
        publisher = '三立新聞網'
        for i in range(len(titles)):
            title = titles[i].text
            dateString = dates[i].text
            url = 'https://www.setn.com/' + url_tag[i].get('href').replace('&From=Search','')
            dateFormatter = "%Y/%m/%d %H:%M"
            published_date = datetime.strptime(dateString, dateFormatter)
            expect_time = datetime.today() - timedelta(hours=1)
            if len(self.env['news_crawler'].search([("url","=",url)])) == 0  and len(self.env['news_crawler'].search([("name","=",title)])) == 0:
                if published_date >= expect_time:
                    create_record = self.create({
                                'id':1,
                                'name': title,
                                'publisher': publisher,
                                'url':url,
                                'date': published_date - timedelta(hours=8)
                    })
                    self.env.cr.commit()
                    if create_record:
                        #發送 Line Notify 訊息
                        token = self.env['config_token'].search([('env_name','=','here')]).line_token  # MySelf
                        self.lineNotify(token, title + " " + url)
    def get_ettoday_news(self,keyword): # not Article
        url = 'https://www.ettoday.net/news_search/doSearch.php?search_term_string=%E5%9F%BA%E9%80%B2'
        headers = {
            'authority': 'www.ettoday.net',
            'method': 'GET',
            'path': '/news_search/doSearch.php?search_term_string=%E5%9F%BA%E9%80%B2',
            'scheme': 'https',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'referer': 'https://www.ettoday.net/news_search/doSearch.php?keywords=',
            'sec-ch-ua': '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36'
        }
        res = requests.get(url=url,headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        titles = soup.select('h2 > a')
        date = soup.select('span.date')
        for i in range(len(titles)):
            title = titles[i].text
            url = titles[i].get('href')
            publish = date[i].text.split('/')[1].replace(' ','')
            dateFormatter = "%Y-%m-%d%H:%M)"
            published_date = datetime.strptime(publish, dateFormatter)
            if len(self.env['news_crawler'].search([("url","=",url)])) == 0  and len(self.env['news_crawler'].search([("name","=",title)])) == 0:
                expect_time = datetime.today() - timedelta(hours=1)
                if published_date >= expect_time:
                    create_record = self.create({
                                'id':1,
                                'name': title,
                                'publisher': 'ETtoday新聞雲',
                                'url':url,
                                'date': published_date - timedelta(hours=8)
                    })
                    self.env.cr.commit()
                    if create_record:
                        #發送 Line Notify 訊息
                        token = self.env['config_token'].search([('env_name','=','here')]).line_token  # MySelf
                        self.lineNotify(token, title + " " + url)
    def get_TVBS_news(self,keyword): # not Article
        url = 'https://news.tvbs.com.tw/news/searchresult/%E5%9F%BA%E9%80%B2/news'
        headers = {
            'authority': 'news.tvbs.com.tw',
            'method': 'GET',
            'path': '/news/searchresult/%E5%9F%BA%E9%80%B2/news',
            'scheme': 'https',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'sec-ch-ua': '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36'
        }
        res = requests.get(url=url,headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        titles = soup.select('h2.search_list_txt')
        urls = soup.select('span.search_list_box > a')
        dates = soup.select('span.publish_date')
        for i in range(len(titles)):
            title = titles[i].text
            url = urls[i].get('href')
            publish = dates[i].text
            dateFormatter = "%Y/%m/%d %H:%M"
            published_date = datetime.strptime(publish, dateFormatter)
            if len(self.env['news_crawler'].search([("url","=",url)])) == 0  and len(self.env['news_crawler'].search([("name","=",title)])) == 0:
                expect_time = datetime.today() - timedelta(hours=1)
                if published_date >= expect_time:
                    create_record = self.create({
                                'id':1,
                                'name': title,
                                'publisher': 'TVBS新聞網',
                                'url':url,
                                'date': published_date - timedelta(hours=8)
                    })
                    self.env.cr.commit()
                    if create_record:
                        #發送 Line Notify 訊息
                        token = self.env['config_token'].search([('env_name','=','here')]).line_token  # MySelf
                        self.lineNotify(token, title + " " + url)
    def get_china_news(self,keyword):# not Article
        links = ['https://www.chinatimes.com/search/%E9%99%B3%E6%9F%8F%E6%83%9F?chdtv','https://www.chinatimes.com/search/%E5%9F%BA%E9%80%B2?chdtv']
        headers = {
            'authority': 'www.chinatimes.com',
            'method': 'GET',
            'scheme': 'https',
            'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'sec-ch-ua': '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36'
        }
        for link in links:
            res = requests.get(url=link,headers=headers)
            soup = BeautifulSoup(res.text, 'html.parser')
            titles = soup.select('h3 > a')
            dates = soup.select('time')
            publisher = '中時新聞網'
            for i in range(len(titles)):
                title = titles[i].text
                url = titles[i].get('href')
                dateString = dates[i].get('datetime')
                dateFormatter = "%Y-%m-%d %H:%M"
                published_date = datetime.strptime(dateString, dateFormatter)
                expect_time = datetime.today() - timedelta(hours=1)
                if len(self.env['news_crawler'].search([("url","=",url)])) == 0  and len(self.env['news_crawler'].search([("name","=",title)])) == 0:
                    if published_date >= expect_time:
                        create_record = self.create({
                                    'id':1,
                                    'name': title,
                                    'publisher': publisher,
                                    'url':url,
                                    'date': published_date - timedelta(hours=8)
                        })
                        self.env.cr.commit()
                        if create_record:
                            #發送 Line Notify 訊息
                            token = self.env['config_token'].search([('env_name','=','here')]).line_token  # MySelf
                            self.lineNotify(token, title + " " + url)
    def get_storm_news(self,keyword): # not Article
        url = 'https://www.storm.mg/site-search/result?q='+ keyword +'&order=none&format=week'
        headers = {
            'authority': 'www.storm.mg',
            'method': 'GET',
            'scheme': 'https',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36'
        }
        res = requests.get(url=url,headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        titles = soup.select('p.card_title')
        urls = soup.select('a.card_substance')
        publish_dates = soup.select('span.info_time')
        
        for i in range(len(titles)):
            title = titles[i].text
            url = 'https://www.storm.mg' + urls[i].get('href')
            publish_date = publish_dates[i].text
            dateFormatter = "%Y-%m-%d %H:%M"
            published_date = datetime.strptime(publish_date, dateFormatter)
            expect_time = datetime.today() - timedelta(hours=1)
            if len(self.env['news_crawler'].search([("url","=",url)])) == 0  and len(self.env['news_crawler'].search([("name","=",title)])) == 0:
                if published_date >= expect_time:
                    create_record = self.create({
                                        'id':1,
                                        'name': title,
                                        'publisher': '風傳媒',
                                        'url':url,
                                        'date': published_date - timedelta(hours=8)
                                    })
                    self.env.cr.commit()
                    if create_record:
                    #發送 Line Notify 訊息
                        token = self.env['config_token'].search([('env_name','=','here')]).line_token  # MySelf
                        self.lineNotify(token, title + " " + url)
    def get_ttv_news(self,keyword): # not Article
        url = 'https://news.ttv.com.tw/search/' + keyword
        headers = {
            'method': 'GET',
            'scheme': 'https',
            'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'sec-ch-ua': '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36'
        }
        res = requests.get(url=url,headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        titles = soup.select('div.title')
        urls = soup.select('ul > li > a.clearfix')
        publishes = soup.select('div.time')

        for i in range(len(urls)):
            url = 'https://news.ttv.com.tw/'+urls[i].get('href')
            title = titles[i+2].text
            publish = publishes[i].text
            dateFormatter = "%Y/%m/%d %H:%M:%S"
            published_date = datetime.strptime(publish, dateFormatter)
            expect_time = datetime.today() - timedelta(hours=1)
            if len(self.env['news_crawler'].search([("url","=",url)])) == 0  and len(self.env['news_crawler'].search([("name","=",title)])) == 0:
                if published_date >= expect_time:
                    create_record = self.create({
                                        'id':1,
                                        'name': title,
                                        'publisher': '台視新聞網',
                                        'url':url,
                                        'date': published_date - timedelta(hours=8)})
                    self.env.cr.commit()
                    if create_record:
                    #發送 Line Notify 訊息
                        token = self.env['config_token'].search([('env_name','=','here')]).line_token  # MySelf
                        self.lineNotify(token, title + " " + url)
    def get_ftv_news(self,keyword): # not Article
        url = 'https://www.ftvnews.com.tw/search/' + keyword
        headers = {
            'method': 'GET',
            'scheme': 'https',
            'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'sec-ch-ua': '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36'
        }
        res = requests.get(url=url,headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        titles = soup.select('div.title')
        urls = soup.select('ul > li > a.clearfix')
        publishes = soup.select('div.time')
        for i in range(len(urls)):
            url = 'https://www.ftvnews.com.tw/'+urls[i].get('href')
            title = titles[i].text
            publish = publishes[i].text
            dateFormatter = "%Y/%m/%d %H:%M:%S"
            published_date = datetime.strptime(publish, dateFormatter)
            expect_time = datetime.today() - timedelta(hours=1)
            if len(self.env['news_crawler'].search([("url","=",url)])) == 0  and len(self.env['news_crawler'].search([("name","=",title)])) == 0:
                if published_date >= expect_time:
                    create_record = self.create({
                                        'id':1,
                                        'name': title,
                                        'publisher': '民視新聞網',
                                        'url':url,
                                        'date': published_date - timedelta(hours=8)})
                    self.env.cr.commit()
                    if create_record:
                    #發送 Line Notify 訊息
                        token = self.env['config_token'].search([('env_name','=','here')]).line_token  # MySelf
                        self.lineNotify(token, title + " " + url)
    def get_cna_news(self,keyword): # not Article
        url = 'https://www.cna.com.tw/search/hysearchws.aspx?q=' + keyword
        headers = {
            'method': 'GET',
            'scheme': 'https',
            'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'sec-ch-ua': '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36'
        }
        res = requests.get(url=url,headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        urls = soup.select('ul.mainList > li > a')
        titles = soup.select('div.listInfo > h2')
        dates = soup.select('div.date')
        for i in range(len(urls)):
            url = urls[i].get('href')
            title = titles[i].text
            publish = dates[i].text
            dateFormatter = "%Y/%m/%d %H:%M"
            published_date = datetime.strptime(publish, dateFormatter)
            expect_time = datetime.today() - timedelta(hours=1)
            if len(self.env['news_crawler'].search([("url","=",url)])) == 0  and len(self.env['news_crawler'].search([("name","=",title)])) == 0:
                if published_date >= expect_time:
                    create_record = self.create({
                                        'id':1,
                                        'name': title,
                                        'publisher': 'CNA中央社',
                                        'url':url,
                                        'date': published_date - timedelta(hours=8)})
                    self.env.cr.commit()
                    if create_record:
                    #發送 Line Notify 訊息
                        token = self.env['config_token'].search([('env_name','=','here')]).line_token  # MySelf
                        self.lineNotify(token, title + " " + url)