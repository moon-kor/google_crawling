import sqlite3
import re
from datetime import datetime, timedelta
from collections import Counter
import json

class MetadataBasedAnalyzer:
    def __init__(self):
        self.DBName = 'google_news.db'
        self.db = sqlite3.connect(self.DBName, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        
        # 감정 분석 키워드 (간단한 규칙 기반)
        self.sentiment_keywords = {
            'positive': [
                '상승', '급등', '돌파', '신기록', '성장', '확대', '증가', '개선', '호재', '긍정',
                '상향', '강세', '매수', '추천', '기대', '희망', '성공', '돌파', '최고', '최대',
                'rise', 'gain', 'surge', 'jump', 'increase', 'growth', 'positive', 'bullish',
                'upgrade', 'recommend', 'expect', 'hope', 'success', 'breakthrough', 'record'
            ],
            'negative': [
                '하락', '급락', '폭락', '위험', '우려', '부정', '악화', '감소', '축소', '손실',
                '하향', '약세', '매도', '경고', '실패', '위기', '충격', '최저', '최소', '폐쇄',
                'fall', 'drop', 'crash', 'risk', 'concern', 'negative', 'bearish', 'downgrade',
                'sell', 'warning', 'failure', 'crisis', 'shock', 'close', 'bankruptcy'
            ],
            'neutral': [
                '발표', '공개', '진행', '계획', '검토', '논의', '협의', '합의', '체결', '완료',
                'announce', 'release', 'plan', 'review', 'discuss', 'agree', 'complete'
            ]
        }
        
        # 주제별 키워드 분류
        self.topic_keywords = {
            '기술': ['AI', '인공지능', '반도체', '칩', '메모리', '스마트폰', '5G', '6G', '블록체인', '클라우드'],
            '금융': ['주식', '투자', '펀드', '은행', '보험', '증권', '금리', '환율', '부동산', '대출'],
            '경제': ['GDP', '인플레이션', '물가', '수출', '수입', '무역', '고용', '실업률', '소비', '생산'],
            '정치': ['정부', '국회', '법안', '정책', '선거', '외교', '국제', '협정', '조약', '회담'],
            '사회': ['교육', '의료', '환경', '교통', '복지', '안전', '범죄', '사고', '재난', '기부']
        }

    def analyze_news_sentiment(self, title, source=None):
        """뉴스 제목 기반 감정 분석"""
        title_lower = title.lower()
        
        positive_score = 0
        negative_score = 0
        neutral_score = 0
        
        # 감정 키워드 카운트
        for keyword in self.sentiment_keywords['positive']:
            if keyword.lower() in title_lower:
                positive_score += 1
        
        for keyword in self.sentiment_keywords['negative']:
            if keyword.lower() in title_lower:
                negative_score += 1
        
        for keyword in self.sentiment_keywords['neutral']:
            if keyword.lower() in title_lower:
                neutral_score += 1
        
        # 감정 판정
        if positive_score > negative_score and positive_score > neutral_score:
            return 'positive', positive_score
        elif negative_score > positive_score and negative_score > neutral_score:
            return 'negative', negative_score
        elif neutral_score > 0:
            return 'neutral', neutral_score
        else:
            return 'unknown', 0

    def classify_news_topic(self, title):
        """뉴스 제목 기반 주제 분류"""
        title_lower = title.lower()
        topic_scores = {}
        
        for topic, keywords in self.topic_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword.lower() in title_lower:
                    score += 1
            if score > 0:
                topic_scores[topic] = score
        
        if topic_scores:
            # 가장 높은 점수의 주제 반환
            return max(topic_scores.items(), key=lambda x: x[1])[0]
        else:
            return '기타'

    def extract_key_entities(self, title):
        """뉴스 제목에서 주요 엔티티 추출"""
        entities = {
            'companies': [],
            'people': [],
            'locations': [],
            'numbers': []
        }
        
        # 회사명 패턴 (대문자 + 주식회사, (주), Corp, Inc 등)
        company_patterns = [
            r'[A-Z가-힣]+(?:주식회사|㈜|㈐|Corp|Inc|Ltd|LLC)',
            r'[A-Z가-힣]+(?:그룹|그룹즈|Group)',
            r'[A-Z가-힣]+(?:전자|전기|화학|건설|금융|은행|증권|보험)'
        ]
        
        for pattern in company_patterns:
            matches = re.findall(pattern, title)
            entities['companies'].extend(matches)
        
        # 숫자 패턴
        number_patterns = [
            r'\d+(?:\.\d+)?(?:%|원|달러|억|만|천)',
            r'\d+(?:\.\d+)?(?:조|억|만|천)원',
            r'\d+(?:\.\d+)?(?:%|percent)'
        ]
        
        for pattern in number_patterns:
            matches = re.findall(pattern, title)
            entities['numbers'].extend(matches)
        
        return entities

    def get_news_statistics(self, keyword, days=7):
        """키워드별 뉴스 통계 분석"""
        try:
            table_name = f'google_news_{keyword.lower()}'
            
            # 최근 N일간 뉴스 조회
            query = f"""
            SELECT * FROM {table_name} 
            WHERE published >= datetime('now', '-{days} days')
            ORDER BY published DESC
            """
            
            cursor = self.db.cursor()
            cursor.execute(query)
            news_list = cursor.fetchall()
            
            if not news_list:
                return None
            
            # 기본 통계
            stats = {
                'total_news': len(news_list),
                'date_range': f'최근 {days}일',
                'sources': Counter(),
                'sentiments': Counter(),
                'topics': Counter(),
                'daily_counts': Counter(),
                'entities': {
                    'companies': Counter(),
                    'numbers': Counter()
                }
            }
            
            # 각 뉴스 분석
            for news in news_list:
                title = news['title']
                source = news['source']
                published = news['published']
                
                # 출처별 카운트
                stats['sources'][source] += 1
                
                # 감정 분석
                sentiment, score = self.analyze_news_sentiment(title, source)
                stats['sentiments'][sentiment] += 1
                
                # 주제 분류
                topic = self.classify_news_topic(title)
                stats['topics'][topic] += 1
                
                # 일별 카운트
                try:
                    date = datetime.strptime(published, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
                    stats['daily_counts'][date] += 1
                except:
                    pass
                
                # 엔티티 추출
                entities = self.extract_key_entities(title)
                stats['entities']['companies'].update(entities['companies'])
                stats['entities']['numbers'].update(entities['numbers'])
            
            return stats
            
        except Exception as e:
            print(f"통계 분석 오류: {e}")
            return None

    def generate_news_report(self, keyword, days=7):
        """뉴스 분석 리포트 생성"""
        stats = self.get_news_statistics(keyword, days)
        
        if not stats:
            return f"'{keyword}' 키워드에 대한 뉴스 데이터가 없습니다."
        
        report = f"""
=== {keyword} 뉴스 분석 리포트 (최근 {days}일) ===

📊 기본 통계
• 총 뉴스 수: {stats['total_news']}개
• 분석 기간: {stats['date_range']}

📈 일별 뉴스 발생량
"""
        
        # 일별 통계 (최근 5일)
        for date, count in sorted(stats['daily_counts'].items(), reverse=True)[:5]:
            report += f"• {date}: {count}개\n"
        
        report += f"""
🎭 감정 분석
"""
        total = stats['total_news']
        for sentiment, count in stats['sentiments'].most_common():
            percentage = (count / total) * 100
            sentiment_kr = {'positive': '긍정', 'negative': '부정', 'neutral': '중립', 'unknown': '미분류'}.get(sentiment, sentiment)
            report += f"• {sentiment_kr}: {count}개 ({percentage:.1f}%)\n"
        
        report += f"""
📰 주요 출처
"""
        for source, count in stats['sources'].most_common(5):
            percentage = (count / total) * 100
            report += f"• {source}: {count}개 ({percentage:.1f}%)\n"
        
        report += f"""
🏷️ 주제별 분류
"""
        for topic, count in stats['topics'].most_common():
            percentage = (count / total) * 100
            report += f"• {topic}: {count}개 ({percentage:.1f}%)\n"
        
        report += f"""
🏢 주요 언급 기업
"""
        for company, count in stats['entities']['companies'].most_common(5):
            report += f"• {company}: {count}회\n"
        
        report += f"""
📊 주요 수치
"""
        for number, count in stats['entities']['numbers'].most_common(5):
            report += f"• {number}: {count}회\n"
        
        return report

    def get_trending_keywords(self, keyword, days=7):
        """키워드와 함께 언급되는 트렌딩 키워드 추출"""
        try:
            table_name = f'google_news_{keyword.lower()}'
            
            query = f"""
            SELECT title FROM {table_name} 
            WHERE published >= datetime('now', '-{days} days')
            """
            
            cursor = self.db.cursor()
            cursor.execute(query)
            titles = [row['title'] for row in cursor.fetchall()]
            
            # 제목에서 키워드 추출
            all_words = []
            for title in titles:
                # 특수문자 제거하고 단어 분리
                words = re.findall(r'[가-힣A-Za-z0-9]+', title)
                all_words.extend(words)
            
            # 키워드 빈도 분석 (기본 키워드 제외)
            exclude_words = {keyword.lower(), '뉴스', '기사', '보도', '발표', '공개', '진행'}
            word_counts = Counter(word.lower() for word in all_words if word.lower() not in exclude_words)
            
            return word_counts.most_common(10)
            
        except Exception as e:
            print(f"트렌딩 키워드 추출 오류: {e}")
            return []

# 사용 예시
if __name__ == "__main__":
    analyzer = MetadataBasedAnalyzer()
    
    # 삼성전자 뉴스 분석
    print(analyzer.generate_news_report('삼성전자', 7))
    
    # 트렌딩 키워드 확인
    trending = analyzer.get_trending_keywords('삼성전자', 7)
    print("\n=== 트렌딩 키워드 ===")
    for word, count in trending:
        print(f"• {word}: {count}회") 