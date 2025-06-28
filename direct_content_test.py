import requests
from bs4 import BeautifulSoup
import time
import random
import re
from urllib.parse import urlparse

class DirectContentCrawler:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def extract_content(self, url):
        """웹페이지에서 뉴스 내용 추출"""
        try:
            print(f"내용 추출 시도: {url}")
            
            time.sleep(random.uniform(1, 2))
            
            response = self.session.get(url, timeout=15)
            
            if response.status_code != 200:
                print(f"HTTP 오류: {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 불필요한 요소 제거
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe']):
                element.decompose()
            
            # 사이트별 특화 추출
            content = self.extract_by_site(url, soup)
            if content:
                return content
            
            # 일반적인 패턴으로 추출
            content = self.extract_general(soup)
            if content:
                return content
            
            return None
            
        except Exception as e:
            print(f"내용 추출 오류: {e}")
            return None

    def extract_by_site(self, url, soup):
        """사이트별 특화 추출"""
        domain = urlparse(url).netloc.lower()
        
        # 사이트별 선택자 매핑
        site_selectors = {
            'www.hankyung.com': ['.article-body', '.article-content', '.content', '.article_text'],
            'www.mk.co.kr': ['.article_body', '.article-content', '.content', '.article_text'],
            'www.etnews.com': ['.article_body', '.article-content', '.content', '.article_text'],
            'www.donga.com': ['.article_body', '.article-content', '.content', '.article_text'],
            'www.chosun.com': ['.article_body', '.article-content', '.content', '.article_text'],
            'www.joongang.co.kr': ['.article_body', '.article-content', '.content', '.article_text'],
            'www.khan.co.kr': ['.article_body', '.article-content', '.content', '.article_text'],
            'www.hani.co.kr': ['.article_body', '.article-content', '.content', '.article_text'],
            'www.ohmynews.com': ['.article_body', '.article-content', '.content', '.article_text'],
            'www.zdnet.co.kr': ['.article_body', '.article-content', '.content', '.article_text'],
            'www.it.co.kr': ['.article_body', '.article-content', '.content', '.article_text'],
            'www.inews24.com': ['.article_body', '.article-content', '.content', '.article_text'],
            'www.m-economynews.com': ['.article_body', '.article-content', '.content', '.article_text'],
        }
        
        if domain in site_selectors:
            for selector in site_selectors[domain]:
                elements = soup.select(selector)
                for element in elements:
                    content = element.get_text(strip=True)
                    if len(content) > 100:
                        print(f"사이트별 추출 성공 ({domain}): {len(content)}자")
                        return self.clean_content(content)
        
        return None

    def extract_general(self, soup):
        """일반적인 패턴으로 추출"""
        # 우선순위별 선택자
        selectors = [
            'article',
            '.article-body', '.article-content', '.article-text',
            '.content', '.post-content', '.entry-content',
            '#article-body', '#content', '#post-content',
            '.story-body', '.story-content',
            '.news-content', '.news-body',
            '.main-content', '.main-text',
            '.text-content', '.text-body'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                content = element.get_text(strip=True)
                if len(content) > 100:
                    print(f"일반 패턴 추출 성공 ({selector}): {len(content)}자")
                    return self.clean_content(content)
        
        # p 태그 기반 추출
        paragraphs = soup.find_all('p')
        if paragraphs:
            valid_paragraphs = []
            for p in paragraphs:
                text = p.get_text(strip=True)
                if len(text) > 30:  # 30자 이상인 p 태그만
                    valid_paragraphs.append(text)
            
            if valid_paragraphs:
                content = ' '.join(valid_paragraphs)
                if len(content) > 100:
                    print(f"p 태그 추출 성공: {len(content)}자")
                    return self.clean_content(content)
        
        return None

    def clean_content(self, content):
        """내용 정리"""
        # 불필요한 공백 제거
        content = re.sub(r'\s+', ' ', content).strip()
        
        # 광고나 불필요한 텍스트 제거
        unwanted_patterns = [
            r'광고',
            r'스폰서',
            r'관련기사',
            r'추천기사',
            r'댓글',
            r'공유하기',
            r'저작권',
            r'Copyright',
            r'All rights reserved'
        ]
        
        for pattern in unwanted_patterns:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE)
        
        # 다시 공백 정리
        content = re.sub(r'\s+', ' ', content).strip()
        
        return content[:3000]  # 최대 3000자로 제한

def test_direct_crawling():
    crawler = DirectContentCrawler()
    
    # 실제 뉴스 사이트 URL들 (테스트용)
    test_urls = [
        "https://www.hankyung.com/economy/article/2024122864651",  # 한국경제
        "https://www.mk.co.kr/news/economy/10812345/",  # 매일경제
        "https://www.etnews.com/20241228000123",  # 전자신문
    ]
    
    print("=== 직접 뉴스 사이트 크롤링 테스트 ===")
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n{i}. 테스트 URL: {url}")
        content = crawler.extract_content(url)
        
        if content:
            print(f"성공! 길이: {len(content)}자")
            print(f"내용 미리보기: {content[:200]}...")
        else:
            print("실패: 내용을 추출할 수 없습니다.")
        
        print("-" * 50)

if __name__ == "__main__":
    test_direct_crawling() 