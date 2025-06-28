# file_checker.py - 파일 상태 확인 및 복구

import os
import shutil

def check_current_file():
    """현재 파일 상태 확인"""
    print("🔍 현재 google_news_cron.py 파일 상태 확인")
    print("-" * 50)
    
    try:
        with open('google_news_cron.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        print(f"📄 파일 읽기 성공 (총 {len(lines)}줄)")
        
        # 문제가 있는 줄 찾기
        problem_lines = []
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            # 함수/클래스 밖에 있으면 안 되는 코드들
            problematic_patterns = [
                'for i, data in enumerate(datas)',
                'data[\'content\']',
                'self.dbManager'
            ]
            
            for pattern in problematic_patterns:
                if pattern in line_stripped and not line_stripped.startswith('#'):
                    # 이 줄이 함수나 클래스 안에 있는지 확인
                    indent_level = len(line) - len(line.lstrip())
                    if indent_level < 4:  # 클래스/함수 밖에 있음
                        problem_lines.append((i, line_stripped, pattern))
        
        if problem_lines:
            print("❌ 문제 발견:")
            for line_num, line_content, pattern in problem_lines:
                print(f"   줄 {line_num}: {line_content[:60]}...")
                print(f"   문제: '{pattern}'이 함수 밖에 있음")
            return False
        else:
            print("✅ 기본 구조는 정상입니다")
            return True
            
    except FileNotFoundError:
        print("❌ google_news_cron.py 파일을 찾을 수 없습니다")
        return False
    except Exception as e:
        print(f"❌ 파일 읽기 오류: {e}")
        return False

def find_backup_files():
    """백업 파일 찾기"""
    print("\n🔍 백업 파일 찾기")
    print("-" * 30)
    
    backup_files = []
    for file in os.listdir('.'):
        if file.startswith('google_news_cron_backup') and file.endswith('.py'):
            backup_files.append(file)
    
    if backup_files:
        backup_files.sort(reverse=True)  # 최신순
        print(f"📁 발견된 백업 파일: {len(backup_files)}개")
        for i, backup in enumerate(backup_files, 1):
            print(f"   {i}. {backup}")
        return backup_files
    else:
        print("❌ 백업 파일을 찾을 수 없습니다")
        return []

def restore_from_backup():
    """백업에서 복구"""
    backup_files = find_backup_files()
    
    if not backup_files:
        return False
    
    print(f"\n가장 최신 백업으로 복구하시겠습니까?")
    print(f"파일: {backup_files[0]}")
    
    choice = input("복구하려면 'y', 취소하려면 'n': ").lower()
    
    if choice == 'y':
        try:
            shutil.copy2(backup_files[0], 'google_news_cron.py')
            print(f"✅ {backup_files[0]}에서 복구 완료!")
            return True
        except Exception as e:
            print(f"❌ 복구 실패: {e}")
            return False
    else:
        print("❌ 복구를 취소했습니다")
        return False

def create_clean_version():
    """깨끗한 새 버전 생성"""
    print("\n🔧 깨끗한 새 버전 생성")
    print("-" * 30)
    
    clean_code = '''from apscheduler.schedulers.background import BackgroundScheduler
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
'''
    
    # 현재 파일 백업
    if os.path.exists('google_news_cron.py'):
        backup_name = f'google_news_cron_broken_{datetime.now().strftime("%Y%m%d_%H%M%S")}.py'
        shutil.copy2('google_news_cron.py', backup_name)
        print(f"📁 현재 파일 백업: {backup_name}")
    
    # 새 파일 작성
    with open('google_news_cron.py', 'w', encoding='utf-8') as f:
        f.write(clean_code)
    
    print("✅ 깨끗한 새 버전 생성 완료!")
    return True

def main():
    print("🛠️ 파일 복구 도구")
    print("=" * 40)
    
    # 현재 파일 상태 확인
    file_ok = check_current_file()
    
    if not file_ok:
        print("\n🔧 복구 옵션:")
        print("1. 백업에서 복구")
        print("2. 깨끗한 새 버전 생성")
        print("3. working_crawler.py 사용 (추천)")
        
        choice = input("\n선택하세요 (1-3): ").strip()
        
        if choice == '1':
            restore_from_backup()
        elif choice == '2':
            create_clean_version()
        elif choice == '3':
            print("💡 working_crawler.py를 실행하세요:")
            print("   python working_crawler.py")
        else:
            print("❌ 잘못된 선택입니다")
    else:
        print("✅ 파일 상태가 정상입니다")

if __name__ == "__main__":
    from datetime import datetime
    main()