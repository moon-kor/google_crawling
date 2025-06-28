# database_fixer.py - 데이터베이스 구조 수정 도구

import sqlite3
import os

def fix_database_structure():
    """
    기존 데이터베이스를 새로운 구조로 업데이트
    """
    db_name = 'google_news.db'
    
    print("🔧 데이터베이스 구조 수정 시작...")
    
    # 데이터베이스 연결
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    try:
        # 1. 현재 존재하는 테이블 목록 확인
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"📋 현재 테이블 목록: {[table[0] for table in tables]}")
        
        # 2. google_news로 시작하는 테이블들 찾기
        news_tables = [table[0] for table in tables if table[0].startswith('google_news_')]
        
        if news_tables:
            print(f"🗑️  삭제할 뉴스 테이블: {news_tables}")
            
            # 사용자 확인
            response = input("기존 뉴스 테이블을 삭제하고 새로 생성하시겠습니까? (y/n): ")
            
            if response.lower() == 'y':
                # 3. 기존 뉴스 테이블들 삭제
                for table in news_tables:
                    cursor.execute(f"DROP TABLE IF EXISTS {table}")
                    print(f"   ✅ {table} 삭제 완료")
                
                conn.commit()
                print("🎉 기존 테이블 삭제 완료!")
                print("💡 이제 새로운 크롤러를 실행하면 올바른 구조로 테이블이 생성됩니다.")
                
            else:
                print("❌ 취소되었습니다.")
        else:
            print("ℹ️  삭제할 뉴스 테이블이 없습니다.")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        
    finally:
        conn.close()

def backup_existing_data():
    """
    기존 데이터를 백업 (선택사항)
    """
    db_name = 'google_news.db'
    backup_name = f'google_news_backup_{int(time.time())}.db'
    
    try:
        # 데이터베이스 파일 복사
        import shutil
        shutil.copy2(db_name, backup_name)
        print(f"💾 백업 완료: {backup_name}")
        return backup_name
    except Exception as e:
        print(f"❌ 백업 실패: {e}")
        return None

def migrate_data_with_content_column():
    """
    기존 데이터를 유지하면서 content 컬럼 추가 (고급 방법)
    """
    db_name = 'google_news.db'
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    try:
        # 현재 테이블 목록 확인
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'google_news_%';")
        tables = cursor.fetchall()
        
        for table_tuple in tables:
            table_name = table_tuple[0]
            print(f"🔄 {table_name} 마이그레이션 중...")
            
            # 테이블 구조 확인
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            # content 컬럼이 없으면 추가
            if 'content' not in column_names:
                try:
                    cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN content text")
                    print(f"   ✅ content 컬럼 추가 완료: {table_name}")
                except Exception as e:
                    print(f"   ❌ 컬럼 추가 실패: {e}")
            else:
                print(f"   ℹ️  이미 content 컬럼이 존재: {table_name}")
        
        conn.commit()
        print("🎉 마이그레이션 완료!")
        
    except Exception as e:
        print(f"❌ 마이그레이션 오류: {e}")
    finally:
        conn.close()

def main():
    print("🛠️  Google News 데이터베이스 수정 도구")
    print("=" * 50)
    
    print("\n선택하세요:")
    print("1. 기존 테이블 삭제 후 새로 생성 (추천)")
    print("2. 기존 데이터 유지하며 컬럼 추가 (고급)")
    print("3. 데이터베이스 백업만")
    print("4. 취소")
    
    choice = input("\n번호를 입력하세요 (1-4): ")
    
    if choice == '1':
        # 백업 먼저
        backup_existing_data()
        fix_database_structure()
        
    elif choice == '2':
        backup_existing_data()
        migrate_data_with_content_column()
        
    elif choice == '3':
        backup_existing_data()
        
    elif choice == '4':
        print("👋 종료합니다.")
        
    else:
        print("❌ 잘못된 선택입니다.")

if __name__ == "__main__":
    import time
    main()