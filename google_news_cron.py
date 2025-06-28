# improved_google_news_cron.py
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

class ImprovedGoogleNewsCron():
    def __init__(self):
        print('크론 시작')
        self.scheduler = BackgroundScheduler(job_defaults={'max_instances': 10, 'coalesce': False})
        self.scheduler.start()
        self.dbManager = google_news_dbmanager.GoogleNewsDBManager()
        
        # 웹사이트 차단 방지를 위한 헤더 설정
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def __del__(self): 
        self.stop()

    def get_article_content(self, url):
        """
        뉴스 링크에서 실제 내용을 크롤링하는 함수
        """
        try:
            # 요청 간격을 두어 서버 부하 방지
            time.sleep(random.uniform(1, 3))
            
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # 여러 뉴스 사이트의 본문 추출 패턴
                content_selectors = [
                    'article',  # 일반적인 article 태그
                    '.article-body',  # 클래스명이 article-body인 요소
                    '.content',  # 클래스명이 content인 요소
                    '#article-body',  # ID가 article-body인 요소
                    '.post-content',  # 블로그 형태
                    'div[data-module="ArticleBody"]',  # 특정 속성을 가진 div
                    '.story-body',  # BBC 스타일
                    '.entry-content'  # 워드프레스 스타일
                ]
                
                # 각 선택자를 시도해서 내용 찾기
                for selector in content_selectors:
                    content_element = soup.select_one(selector)
                    if content_element:
                        # 텍스트만 추출하고 불필요한 공백 제거
                        content = content_element.get_text(strip=True)
                        # 내용이 충분히 길면 반환 (최소 100자)
                        if len(content) > 100:
                            return content[:2000]  # 최대 2000자로 제한
                
                # 특정 선택자로 찾지 못한 경우, p 태그들을 모아서 시도
                paragraphs = soup.find_all('p')
                if paragraphs:
                    content = ' '.join([p.get_text(strip=True) for p in paragraphs])
                    if len(content) > 100:
                        return content[:2000]
                
                return "내용을 추출할 수 없습니다."
                
        except Exception as e:
            print(f"내용 크롤링 오류 ({url}): {e}")
            return "내용 크롤링 실패"

    def exec(self, country, keyword):
        print('Google News Cron Start: ' + datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
        URL = 'https://news.google.com/rss/search?q={}+when:1d'.format(keyword)
        
        if country == 'en':
            URL += '&hl=en-NG&gl=NG&ceid=NG:en'
        elif country == 'ko':
            URL += '&hl=ko&gl=KR&ceid=KR:ko'

        try: 
            res = requests.get(URL)
            if res.status_code == 200:
                datas = feedparser.parse(res.text).entries
                
                print(f"총 {len(datas)}개의 뉴스를 발견했습니다.")
                
                for i, data in enumerate(datas):
                    print(f"처리 중: {i+1}/{len(datas)} - {data.title}")
                    
                    # 기존 데이터 처리
                    data['published'] = maya.parse(data.published).datetime(to_timezone="Asia/Seoul", naive=True) 
                    data['source'] = data.source.title
                    
                    # 🔥 새로 추가: 뉴스 내용 크롤링
                    article_content = self.get_article_content(data.link)
                    data['content'] = article_content
                    
                    # 데이터베이스에 저장 (내용 포함)
                    self.dbManager.queryInsertGoogleNewsTable(data)
                    
            else:
                print('Google 검색 에러')
                
        except requests.exceptions.RequestException as err:
            print('Error Requests: {}'.format(err))
    
    def run(self, mode, country, keyword):
        print("실행!")
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
        try: 
            self.scheduler.shutdown() 
        except: 
            pass
        try: 
            self.dbManager.close() 
        except: 
            pass

# 사용 예시
if __name__ == "__main__":
    crawler = ImprovedGoogleNewsCron()
    
    # 한 번만 실행 (테스트용)
    crawler.run('once', 'ko', '삼성전자')
    
    # 프로그램이 종료되지 않도록 대기
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("프로그램을 종료합니다.")
        crawler.stop()