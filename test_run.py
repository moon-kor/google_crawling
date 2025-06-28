from google_news_cron import GoogleNewsCron
import time

def test_google_news_crawling():
    print("=== Google News 크롤링 테스트 시작 ===")
    
    # 크론 객체 생성
    cron = GoogleNewsCron()
    
    try:
        # 테스트 실행 (한 번만 실행)
        print("'삼성전자' 키워드로 한국 뉴스 크롤링 시작...")
        cron.run(mode='once', country='ko', keyword='삼성전자')
        
        # 잠시 대기
        time.sleep(5)
        
        # 데이터베이스에서 결과 확인
        print("\n=== 크롤링 결과 확인 ===")
        results = cron.dbManager.querySelectAllGoogleNewsTable('삼성전자')
        
        if results:
            print(f"총 {len(results)}개의 뉴스가 수집되었습니다:")
            for i, news in enumerate(results[:5], 1):  # 처음 5개만 출력
                print(f"{i}. {news['title']}")
                print(f"   출처: {news['source']}")
                print(f"   링크: {news['link']}")
                print(f"   날짜: {news['published']}")
                print()
        else:
            print("수집된 뉴스가 없습니다.")
            
    except Exception as e:
        print(f"오류 발생: {e}")
    
    finally:
        # 정리
        cron.stop()
        print("=== 테스트 완료 ===")

if __name__ == "__main__":
    test_google_news_crawling() 