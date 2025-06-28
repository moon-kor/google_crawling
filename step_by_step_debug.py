# simple_debug.py - 간단한 문제 확인

import sqlite3
import requests
from bs4 import BeautifulSoup

def check_database_simple():
    """데이터베이스 간단 확인"""
    print("🔍 데이터베이스 확인")
    print("-" * 30)
    
    try:
        conn = sqlite3.connect('google_news.db')
        cursor = conn.cursor()
        
        # 테이블 목록
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in cursor.fetchall()]
        print(f"테이블 목록: {tables}")
        
        # 뉴스 테이블 찾기
        news_tables = [t for t in tables if 'google_news_' in t]
        if not news_tables:
            print("❌ 뉴스 테이블이 없습니다!")
            return
        
        table_name = news_tables[0]
        print(f"확인할 테이블: {table_name}")
        
        # 컬럼 확인
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"컬럼들: {columns}")
        
        if 'content' not in columns:
            print("❌ content 컬럼이 없습니다!")
            print("해결책: 테이블을 삭제하고 다시 만드세요")
            return
        
        # 데이터 확인
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        total = cursor.fetchone()[0]
        print(f"전체 뉴스: {total}개")
        
        cursor.execute(f"SELECT title, content FROM {table_name} LIMIT 3")
        samples = cursor.fetchall()
        
        print("\n샘플 데이터:")
        for i, (title, content) in enumerate(samples, 1):
            print(f"[{i}] {title[:40]}...")
            print(f"    내용: {content[:80] if content else 'None'}...")
            print()
        
        conn.close()
        
    except Exception as e:
        print(f"오류: {e}")

def test_crawling_simple():
    """간단한 크롤링 테스트"""
    print("🔍 크롤링 테스트")
    print("-" * 30)
    
    # 네이버 뉴스 테스트
    test_url = "https://n.news.naver.com/mnews/article/029/0002868791"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        print(f"테스트 URL: {test_url}")
        response = requests.get(test_url, headers=headers, timeout=10)
        print(f"응답 코드: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 네이버 뉴스 본문 찾기
            content_area = soup.select_one('#dic_area')
            if content_area:
                content = content_area.get_text(strip=True)
                print(f"✅ 성공! 길이: {len(content)}자")
                print(f"내용: {content[:100]}...")
            else:
                print("❌ 내용을 찾을 수 없습니다")
        else:
            print("❌ 페이지에 접근할 수 없습니다")
            
    except Exception as e:
        print(f"오류: {e}")

def check_current_code():
    """현재 코드 확인"""
    print("🔍 코드 확인")
    print("-" * 30)
    
    try:
        with open('google_news_cron.py', 'r', encoding='utf-8') as f:
            code = f.read()
        
        print("파일 읽기 성공")
        
        # 중요한 부분들 확인
        checks = [
            ('BeautifulSoup import', 'from bs4 import BeautifulSoup'),
            ('get_content 함수', 'def get_content'),
            ('content 설정', "data['content']"),
            ('content 저장', 'content')
        ]
        
        for name, pattern in checks:
            if pattern in code:
                print(f"✅ {name}: 있음")
            else:
                print(f"❌ {name}: 없음")
        
    except FileNotFoundError:
        print("❌ google_news_cron.py 파일을 찾을 수 없습니다")
    except Exception as e:
        print(f"오류: {e}")

if __name__ == "__main__":
    print("🛠️ 간단한 문제 진단")
    print("=" * 40)
    
    check_database_simple()
    print()
    test_crawling_simple()
    print()
    check_current_code()