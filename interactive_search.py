from google_news_cron import GoogleNewsCron as GoogleNewsCron
import time

def interactive_search():
    print("=== Google News 인터랙티브 검색 ===")
    print("종료하려면 'quit' 또는 'exit'를 입력하세요.")
    
    # 크론 객체 생성
    cron = GoogleNewsCron()
    
    try:
        while True:
            print("\n" + "="*50)
            
            # 키워드 입력
            keyword = input("검색할 키워드를 입력하세요: ").strip()
            
            if keyword.lower() in ['quit', 'exit', '종료']:
                print("검색을 종료합니다.")
                break
            
            if not keyword:
                print("키워드를 입력해주세요.")
                continue
            
            # 국가 선택
            print("\n국가를 선택하세요:")
            print("1. 한국 (ko)")
            print("2. 영어권 (en)")
            
            country_choice = input("선택 (1 또는 2): ").strip()
            
            if country_choice == '1':
                country = 'ko'
                country_name = '한국'
            elif country_choice == '2':
                country = 'en'
                country_name = '영어권'
            else:
                print("잘못된 선택입니다. 한국으로 설정합니다.")
                country = 'ko'
                country_name = '한국'
            
            print(f"\n'{keyword}' 키워드로 {country_name} 뉴스를 검색합니다...")
            
            # 크롤링 실행
            cron.run(mode='once', country=country, keyword=keyword)
            
            # 잠시 대기
            time.sleep(3)
            
            # 결과 확인
            results = cron.dbManager.querySelectAllGoogleNewsTable(keyword)
            print(f"\n총 {len(results)}개의 뉴스가 수집되었습니다.")
            
            if results:
                print("\n수집된 뉴스 목록:")
                for i, news in enumerate(results[:10], 1):  # 처음 10개만 출력
                    print(f"{i:2d}. {news['title']}")
                    print(f"    출처: {news['source']} | 날짜: {news['published']}")
                    print()
                
                if len(results) > 10:
                    print(f"... 외 {len(results) - 10}개 더")
            else:
                print("수집된 뉴스가 없습니다.")
            
            # 계속할지 묻기
            continue_choice = input("\n다른 키워드로 검색하시겠습니까? (y/n): ").strip().lower()
            if continue_choice not in ['y', 'yes', '예', 'ㅇ']:
                break
                
    except KeyboardInterrupt:
        print("\n\n검색이 중단되었습니다.")
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 정리
        cron.stop()
        print("=== 검색 완료 ===")

if __name__ == "__main__":
    interactive_search() 