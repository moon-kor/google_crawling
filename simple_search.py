from google_news_cron import GoogleNewsCron
import sys
import time

def simple_search(keyword, country='ko'):
    """
    간단한 키워드 검색
    사용법: python simple_search.py "키워드" [국가]
    국가: ko (한국, 기본값) 또는 en (영어권)
    """
    print(f"=== '{keyword}' 키워드로 {country} 뉴스 검색 ===")
    
    # 크론 객체 생성
    cron = GoogleNewsCron()
    
    try:
        # 크롤링 실행
        cron.run(mode='once', country=country, keyword=keyword)
        
        # 잠시 대기
        time.sleep(3)
        
        # 결과 확인
        results = cron.dbManager.querySelectAllGoogleNewsTable(keyword)
        print(f"\n총 {len(results)}개의 뉴스가 수집되었습니다.")
        
        if results:
            print("\n수집된 뉴스:")
            for i, news in enumerate(results[:5], 1):  # 처음 5개만 출력
                print(f"{i}. {news['title']}")
                print(f"   출처: {news['source']}")
                print(f"   날짜: {news['published']}")
                print()
        else:
            print("수집된 뉴스가 없습니다.")
            
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 정리
        cron.stop()
        print("=== 검색 완료 ===")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python simple_search.py '키워드' [국가]")
        print("예시: python simple_search.py '삼성전자' ko")
        print("예시: python simple_search.py 'Apple' en")
        sys.exit(1)
    
    keyword = sys.argv[1]
    country = sys.argv[2] if len(sys.argv) > 2 else 'ko'
    
    if country not in ['ko', 'en']:
        print("국가는 'ko' 또는 'en'만 사용 가능합니다.")
        sys.exit(1)
    
    simple_search(keyword, country) 