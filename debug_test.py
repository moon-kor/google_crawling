from google_news_cron import GoogleNewsCron
import time

def debug_google_news_crawling():
    print("=== Google News 크롤링 디버그 테스트 시작 ===")
    
    # 크론 객체 생성
    cron = GoogleNewsCron()
    
    try:
        # 테스트 실행 (한 번만 실행)
        print("'삼성전자' 키워드로 한국 뉴스 크롤링 시작...")
        cron.run(mode='once', country='ko', keyword='삼성전자')
        
        # 잠시 대기
        print("5초 대기 중...")
        time.sleep(5)
        
        # 데이터베이스에서 결과 확인
        print("\n=== 크롤링 결과 확인 ===")
        results = cron.dbManager.querySelectAllGoogleNewsTable('삼성전자')
        
        print(f"데이터베이스에서 가져온 결과 수: {len(results)}")
        
        if results:
            print(f"총 {len(results)}개의 뉴스가 수집되었습니다:")
            for i, news in enumerate(results[:3], 1):  # 처음 3개만 출력
                print(f"{i}. 제목: {news['title']}")
                print(f"   출처: {news['source']}")
                print(f"   링크: {news['link']}")
                print(f"   날짜: {news['published']}")
                print()
        else:
            print("수집된 뉴스가 없습니다.")
            
        # 키워드 테이블도 확인
        print("\n=== 키워드 테이블 확인 ===")
        keywords = cron.dbManager.querySelectAllKeywordTable()
        print(f"키워드 테이블에 저장된 키워드 수: {len(keywords)}")
        for kw in keywords:
            print(f"키워드: {kw['keyword']}, 국가: {kw['country']}")
            
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 정리
        cron.stop()
        print("=== 디버그 테스트 완료 ===")

if __name__ == "__main__":
    debug_google_news_crawling() 