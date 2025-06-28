from google_news_cron import GoogleNewsCron
import time

def test_multiple_keywords():
    print("=== 여러 키워드로 Google News 크롤링 테스트 ===")
    
    # 크론 객체 생성
    cron = GoogleNewsCron()
    
    # 검색할 키워드 리스트
    keywords = [
        ('SK하이닉스', 'ko'),
        ('LG전자', 'ko'), 
        ('Apple', 'en'),
        ('Tesla', 'en')
    ]
    
    try:
        for keyword, country in keywords:
            print(f"\n=== '{keyword}' 키워드로 {country} 뉴스 크롤링 시작 ===")
            
            # 크롤링 실행
            cron.run(mode='once', country=country, keyword=keyword)
            
            # 잠시 대기
            time.sleep(3)
            
            # 결과 확인
            results = cron.dbManager.querySelectAllGoogleNewsTable(keyword)
            print(f"수집된 뉴스 수: {len(results)}")
            
            if results:
                print("샘플 뉴스:")
                for i, news in enumerate(results[:2], 1):  # 처음 2개만 출력
                    print(f"  {i}. {news['title']}")
                    print(f"     출처: {news['source']}")
                    print(f"     날짜: {news['published']}")
                    print()
            
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 정리
        cron.stop()
        print("=== 모든 키워드 테스트 완료 ===")

if __name__ == "__main__":
    test_multiple_keywords() 