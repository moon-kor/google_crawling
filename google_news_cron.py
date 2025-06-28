from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.base import JobLookupError
import requests
import datetime
import maya
import feedparser
from bs4 import BeautifulSoup
import time
import random

import google_news_dbmanager

class GoogleNewsCron():
    def __init__(self):
        print ('크론 시작')
        self.scheduler = BackgroundScheduler(job_defaults={'max_instances': 10, 'coalesce': False})
        self.scheduler.start()
        self.dbManager = google_news_dbmanager.GoogleNewsDBManager()

    def __del__(self): 
        self.stop()

    def get_content(self, url):
        """뉴스 내용 크롤링 함수"""
        print(f"   📄 내용 크롤링: {url[:50]}...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        try:
            time.sleep(random.uniform(1, 2))
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                selectors = [
                    '#dic_area',        # 네이버 뉴스
                    '.article_view',    # 다음 뉴스
                    '.article-body',    # 일반적인 패턴
                    '.article_body',    # 변형
                    'article',          # HTML5 article 태그
                    '.content',         # 일반적인 content 클래스
                    '.post-content',    # 블로그 스타일
                    '.entry-content'    # 워드프레스
                ]
                
                for selector in selectors:
                    element = soup.select_one(selector)
                    if element:
                        content = element.get_text(strip=True)
                        if len(content) > 100:
                            print(f"   ✅ 성공! 길이: {len(content)}자")
                            return content[:1500]
                
                paragraphs = soup.find_all('p')
                if paragraphs:
                    content = ' '.join([p.get_text(strip=True) for p in paragraphs])
                    if len(content) > 100:
                        print(f"   ✅ p태그로 성공! 길이: {len(content)}자")
                        return content[:1500]
                
                print("   ❌ 내용 추출 실패")
                return "내용 추출 실패"
                
            else:
                print(f"   ❌ HTTP {response.status_code}")
                return "접근 실패"
                
        except Exception as e:
            print(f"   ❌ 오류: {str(e)[:30]}")
            return "크롤링 오류"

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
                print(f"📰 총 {len(datas)}개 뉴스 발견")
                
                for i, data in enumerate(datas):
                    print(f"처리 중: {i+1}/{len(datas)} - {data.title}")
                    data['published'] = maya.parse(data.published).datetime(to_timezone="Asia/Seoul", naive=True) 
                    data['source'] = data.source.title
                    data['content'] = self.get_content(data.link)
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
