from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.base import JobLookupError
import requests
import datetime
import maya
import feedparser

import google_news_dbmanager

class GoogleNewsCron():
    def __init__(self):
        print ('크론 시작')
        self.scheduler = BackgroundScheduler(job_defaults={'max_instances': 10, 'coalesce': False})
        self.scheduler.start()
        self.dbManager = google_news_dbmanager.GoogleNewsDBManager()

    def __del__(self): 
        self.stop()

    def exec(self, country, keyword):
        print ('Google News Cron Start: ' + datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
        URL = 'https://news.google.com/rss/search?q={}+when:1d'.format(keyword)
        if country == 'en':
            URL += '&hl=en-NG&gl=NG&ceid=NG:en'
        elif country == 'ko':
            URL += '&hl=ko&gl=KR&ceid=KR:ko'

        try: 
            res = requests.get(URL)
            if res.status_code == 200:
                datas = feedparser.parse(res.text).entries
                for data in datas:
                    data['published'] = maya.parse(data.published).datetime(to_timezone="Asia/Seoul", naive=True) 
                    data['source'] = data.source.title
                    self.dbManager.queryInsertGoogleNewsTable(data)
            else:
                print ('Google 검색 에러')
        except requests.exceptions.RequestException as err:
            print ('Error Requests: {}'.format(err))
    
    def run(self, mode, country, keyword):
        print ("실행!")
        self.dbManager.queryCreateGoogleNewsTable(keyword)
        self.dbManager.queryCreateKeywordTable()
        self.dbManager.queryInsertKeywordTable({
            'keyword': keyword,
            'country': country
        })
        if mode == 'once':
            self.scheduler.add_job(self.exec, args=[country, keyword])
        elif mode == 'interval':
            self.scheduler.add_job(self.exec, 'interval', seconds=10, args=[country, keyword])
        elif mode == 'cron':
            self.scheduler.add_job(self.exec, 'cron', second='*/10', args=[country, keyword])

    def stop(self):
        try: self.scheduler.shutdown() 
        except: pass
        try: self.dbManager.close() 
        except: pass