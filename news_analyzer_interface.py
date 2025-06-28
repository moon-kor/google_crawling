from metadata_based_analyzer import MetadataBasedAnalyzer
import time

class NewsAnalyzerInterface:
    def __init__(self):
        self.analyzer = MetadataBasedAnalyzer()
        
    def show_menu(self):
        """메인 메뉴 표시"""
        print("\n" + "="*60)
        print("📰 뉴스 메타데이터 분석 시스템")
        print("="*60)
        print("1. 키워드별 뉴스 분석 리포트")
        print("2. 감정 분석 결과")
        print("3. 주제별 분류 통계")
        print("4. 트렌딩 키워드 확인")
        print("5. 주요 언급 기업/수치")
        print("6. 일별 뉴스 발생량")
        print("7. 전체 분석 리포트 생성")
        print("0. 종료")
        print("="*60)
    
    def get_keyword_input(self):
        """키워드 입력 받기"""
        while True:
            keyword = input("\n분석할 키워드를 입력하세요: ").strip()
            if keyword:
                return keyword
            print("키워드를 입력해주세요.")
    
    def get_days_input(self):
        """분석 기간 입력 받기"""
        while True:
            try:
                days = input("분석 기간을 입력하세요 (기본값: 7일): ").strip()
                if not days:
                    return 7
                days = int(days)
                if 1 <= days <= 30:
                    return days
                print("1-30일 사이의 값을 입력해주세요.")
            except ValueError:
                print("숫자를 입력해주세요.")
    
    def show_sentiment_analysis(self, keyword, days):
        """감정 분석 결과 표시"""
        print(f"\n🎭 {keyword} 감정 분석 결과 (최근 {days}일)")
        print("-" * 50)
        
        stats = self.analyzer.get_news_statistics(keyword, days)
        if not stats:
            print("데이터가 없습니다.")
            return
        
        total = stats['total_news']
        sentiment_names = {
            'positive': '긍정',
            'negative': '부정', 
            'neutral': '중립',
            'unknown': '미분류'
        }
        
        for sentiment, count in stats['sentiments'].most_common():
            percentage = (count / total) * 100
            name = sentiment_names.get(sentiment, sentiment)
            bar = "█" * int(percentage / 2)  # 시각적 바 차트
            print(f"{name:>6}: {count:>3}개 ({percentage:>5.1f}%) {bar}")
    
    def show_topic_analysis(self, keyword, days):
        """주제별 분류 통계 표시"""
        print(f"\n🏷️ {keyword} 주제별 분류 (최근 {days}일)")
        print("-" * 50)
        
        stats = self.analyzer.get_news_statistics(keyword, days)
        if not stats:
            print("데이터가 없습니다.")
            return
        
        total = stats['total_news']
        for topic, count in stats['topics'].most_common():
            percentage = (count / total) * 100
            bar = "█" * int(percentage / 2)
            print(f"{topic:>6}: {count:>3}개 ({percentage:>5.1f}%) {bar}")
    
    def show_trending_keywords(self, keyword, days):
        """트렌딩 키워드 표시"""
        print(f"\n🔥 {keyword} 관련 트렌딩 키워드 (최근 {days}일)")
        print("-" * 50)
        
        trending = self.analyzer.get_trending_keywords(keyword, days)
        if not trending:
            print("트렌딩 키워드가 없습니다.")
            return
        
        for i, (word, count) in enumerate(trending, 1):
            print(f"{i:2d}. {word:>15}: {count:>3}회")
    
    def show_entities(self, keyword, days):
        """주요 언급 기업/수치 표시"""
        print(f"\n📊 {keyword} 주요 언급 정보 (최근 {days}일)")
        print("-" * 50)
        
        stats = self.analyzer.get_news_statistics(keyword, days)
        if not stats:
            print("데이터가 없습니다.")
            return
        
        print("🏢 주요 언급 기업:")
        for company, count in stats['entities']['companies'].most_common(5):
            print(f"  • {company}: {count}회")
        
        print("\n📈 주요 수치:")
        for number, count in stats['entities']['numbers'].most_common(5):
            print(f"  • {number}: {count}회")
    
    def show_daily_counts(self, keyword, days):
        """일별 뉴스 발생량 표시"""
        print(f"\n📈 {keyword} 일별 뉴스 발생량 (최근 {days}일)")
        print("-" * 50)
        
        stats = self.analyzer.get_news_statistics(keyword, days)
        if not stats:
            print("데이터가 없습니다.")
            return
        
        for date, count in sorted(stats['daily_counts'].items(), reverse=True):
            bar = "█" * min(count, 20)  # 최대 20개까지 표시
            print(f"{date}: {count:>3}개 {bar}")
    
    def show_full_report(self, keyword, days):
        """전체 분석 리포트 표시"""
        print(f"\n📋 {keyword} 전체 분석 리포트 생성 중...")
        report = self.analyzer.generate_news_report(keyword, days)
        print(report)
        
        # 파일로 저장
        filename = f"{keyword}_뉴스분석_{days}일.txt"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"\n✅ 리포트가 '{filename}' 파일로 저장되었습니다.")
        except Exception as e:
            print(f"파일 저장 실패: {e}")
    
    def run(self):
        """메인 실행 루프"""
        while True:
            self.show_menu()
            
            try:
                choice = input("\n선택하세요 (0-7): ").strip()
                
                if choice == '0':
                    print("프로그램을 종료합니다.")
                    break
                
                elif choice == '1':
                    keyword = self.get_keyword_input()
                    days = self.get_days_input()
                    print(f"\n📰 {keyword} 뉴스 분석 리포트 (최근 {days}일)")
                    print("-" * 50)
                    stats = self.analyzer.get_news_statistics(keyword, days)
                    if stats:
                        print(f"총 뉴스 수: {stats['total_news']}개")
                        print(f"분석 기간: {stats['date_range']}")
                    else:
                        print("데이터가 없습니다.")
                
                elif choice == '2':
                    keyword = self.get_keyword_input()
                    days = self.get_days_input()
                    self.show_sentiment_analysis(keyword, days)
                
                elif choice == '3':
                    keyword = self.get_keyword_input()
                    days = self.get_days_input()
                    self.show_topic_analysis(keyword, days)
                
                elif choice == '4':
                    keyword = self.get_keyword_input()
                    days = self.get_days_input()
                    self.show_trending_keywords(keyword, days)
                
                elif choice == '5':
                    keyword = self.get_keyword_input()
                    days = self.get_days_input()
                    self.show_entities(keyword, days)
                
                elif choice == '6':
                    keyword = self.get_keyword_input()
                    days = self.get_days_input()
                    self.show_daily_counts(keyword, days)
                
                elif choice == '7':
                    keyword = self.get_keyword_input()
                    days = self.get_days_input()
                    self.show_full_report(keyword, days)
                
                else:
                    print("잘못된 선택입니다. 0-7 사이의 숫자를 입력하세요.")
                
                input("\n계속하려면 Enter를 누르세요...")
                
            except KeyboardInterrupt:
                print("\n\n프로그램을 종료합니다.")
                break
            except Exception as e:
                print(f"오류 발생: {e}")
                input("계속하려면 Enter를 누르세요...")

# 사용 예시
if __name__ == "__main__":
    interface = NewsAnalyzerInterface()
    interface.run() 