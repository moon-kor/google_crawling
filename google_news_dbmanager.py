# improved_google_news_dbmanager.py
import sqlite3

class GoogleNewsDBManager:
    def __init__(self):
        print("DB Manager 시작")
        self.DBName = 'google_news.db'
        self.db = sqlite3.connect(self.DBName, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.google_news_table = 'google_news'
        self.keyword_table = 'keyword'
        
        # 🔥 개선점: content 컬럼 추가
        self.google_news_columns = {
            'published': 'text',
            'source': 'text',
            'title': 'text',
            'link': 'text PRIMARY KEY',  # link를 PRIMARY KEY로 변경 (중복 방지)
            'content': 'text'  # 📝 뉴스 내용 저장용 컬럼 추가
        }
        
        self.keyword_columns = {
            'keyword': 'text PRIMARY KEY',
            'country': 'text',
        }

    def __del__(self):
        self.stop()

    def stop(self):
        try: 
            self.db.close()
        except: 
            pass
    
    def queryCreateGoogleNewsTable(self, keyword):
        """
        키워드별로 뉴스 테이블 생성
        """
        self.google_news_table = 'google_news_' + keyword.lower()
        cursor = self.db.cursor()
        
        # 컬럼 정보를 문자열로 변환
        colum_info = ",".join(col_name + ' ' + col_type for col_name, col_type in self.google_news_columns.items())
        query = "CREATE TABLE IF NOT EXISTS {} ({})".format(self.google_news_table, colum_info)
        
        cursor.execute(query)
        self.db.commit()
        print(f"테이블 생성 완료: {self.google_news_table}")

    def queryInsertGoogleNewsTable(self, values):
        """
        뉴스 데이터를 데이터베이스에 삽입
        """
        cursor = self.db.cursor()
        
        # 컬럼명들을 문자열로 조합
        columns = ','.join(self.google_news_columns.keys())
        
        # 값들을 안전하게 처리 (SQL Injection 방지)
        placeholders = ','.join(['?' for _ in self.google_news_columns.keys()])
        
        # 각 컬럼에 해당하는 값들을 순서대로 추출
        values_list = []
        for col_name in self.google_news_columns.keys():
            if col_name in values:
                # 문자열에서 따옴표 문제 해결
                value = str(values[col_name]).replace('"', "'").replace("'", "''")
                values_list.append(value)
            else:
                values_list.append("")  # 값이 없으면 빈 문자열
        
        query = f'INSERT OR REPLACE INTO {self.google_news_table} ({columns}) VALUES ({placeholders})'
        
        try:
            cursor.execute(query, values_list)
            self.db.commit()
            print(f"데이터 저장 완료: {values.get('title', 'Unknown')[:50]}...")
        except Exception as e:
            print(f"데이터 저장 오류: {e}")

    def querySelectAllGoogleNewsTable(self, keyword):
        """
        특정 키워드의 모든 뉴스 조회
        """
        google_news_table = 'google_news_' + keyword.lower()
        query = f"SELECT * FROM {google_news_table} ORDER BY published DESC"
        cursor = self.db.cursor()
        cursor.execute(query)
        return cursor.fetchall()

    def querySelectNewsWithContent(self, keyword, limit=10):
        """
        🔥 새로운 기능: 내용이 있는 뉴스만 조회
        """
        google_news_table = 'google_news_' + keyword.lower()
        query = f"""
        SELECT * FROM {google_news_table} 
        WHERE content IS NOT NULL 
        AND content != '' 
        AND content != '내용을 추출할 수 없습니다.'
        AND content != '내용 크롤링 실패'
        ORDER BY published DESC 
        LIMIT ?
        """
        cursor = self.db.cursor()
        cursor.execute(query, (limit,))
        return cursor.fetchall()

    def querySearchNews(self, keyword, search_term):
        """
        🔥 새로운 기능: 제목이나 내용에서 특정 단어 검색
        """
        google_news_table = 'google_news_' + keyword.lower()
        query = f"""
        SELECT * FROM {google_news_table} 
        WHERE title LIKE ? OR content LIKE ?
        ORDER BY published DESC
        """
        cursor = self.db.cursor()
        search_pattern = f'%{search_term}%'
        cursor.execute(query, (search_pattern, search_pattern))
        return cursor.fetchall()

    def queryGetNewsStats(self, keyword):
        """
        🔥 새로운 기능: 뉴스 통계 정보
        """
        google_news_table = 'google_news_' + keyword.lower()
        cursor = self.db.cursor()
        
        # 전체 뉴스 수
        cursor.execute(f"SELECT COUNT(*) FROM {google_news_table}")
        total_count = cursor.fetchone()[0]
        
        # 내용이 있는 뉴스 수
        cursor.execute(f"""
        SELECT COUNT(*) FROM {google_news_table} 
        WHERE content IS NOT NULL 
        AND content != '' 
        AND content != '내용을 추출할 수 없습니다.'
        AND content != '내용 크롤링 실패'
        """)
        content_count = cursor.fetchone()[0]
        
        return {
            'total_news': total_count,
            'news_with_content': content_count,
            'success_rate': (content_count / total_count * 100) if total_count > 0 else 0
        }

    # 기존 키워드 테이블 관련 메서드들
    def queryCreateKeywordTable(self):
        cursor = self.db.cursor()
        colum_info = ",".join(col_name + ' ' + col_type for col_name, col_type in self.keyword_columns.items())
        query = f"CREATE TABLE IF NOT EXISTS {self.keyword_table} ({colum_info})"
        cursor.execute(query)
        self.db.commit()

    def queryInsertKeywordTable(self, values):
        cursor = self.db.cursor()
        columns = ','.join(self.keyword_columns.keys())
        values_str = '","'.join(str(values[col_name]).replace('"',"'") for col_name in self.keyword_columns.keys())
        query = f'INSERT OR IGNORE INTO {self.keyword_table} ({columns}) VALUES ("{values_str}")'
        cursor.execute(query)
        self.db.commit()

    def queryDeleteKeywordTable(self, keyword):
        cursor = self.db.cursor()
        query = f"DELETE FROM {self.keyword_table} WHERE KEYWORD='{keyword}'"
        cursor.execute(query)
        self.db.commit()

    def querySelectAllKeywordTable(self):
        query = f"SELECT * FROM {self.keyword_table}"
        cursor = self.db.cursor()
        cursor.execute(query)
        return cursor.fetchall()

    def queryDeleteAllGoogleNewsTable(self, keyword):
        google_news_table = 'google_news_' + keyword.lower()
        query = f"DROP TABLE IF EXISTS {google_news_table}"
        cursor = self.db.cursor()
        cursor.execute(query)
        self.db.commit()

# 🔥 데이터베이스 조회 예시 코드
if __name__ == "__main__":
    db = GoogleNewsDBManager()
    
    # 통계 확인
    stats = db.queryGetNewsStats('삼성전자')
    print(f"전체 뉴스: {stats['total_news']}개")
    print(f"내용 포함 뉴스: {stats['news_with_content']}개")
    print(f"성공률: {stats['success_rate']:.1f}%")
    
    # 내용이 있는 뉴스 5개 조회
    news_list = db.querySelectNewsWithContent('삼성전자', 5)
    for news in news_list:
        print(f"\n제목: {news['title']}")
        print(f"내용: {news['content'][:100]}...")  # 처음 100자만