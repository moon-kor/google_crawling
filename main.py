import sqlite3

class GoogleNewsDBManager:
    def __init__(self):
        print ("DB Manager 시작")
        self.DBName = 'google_news.db'
        self.db = sqlite3.connect(self.DBName, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.google_news_table = 'google_news'
        self.keyword_table = 'keyword'
        self.google_news_columns = {
            'published': 'text',
            'source': 'text PRIMARY KEY',
            'title': 'text',
            'link': 'text',
        }
        self.keyword_columns = {
            'keyword': 'text PRIMARY KEY',
            'country': 'text',
        }

    def __del__(self):
        self.stop()

    def stop(self):
        try: self.db.close()
        except: pass
    
    def queryCreateGoogleNewsTable(self, keyword):
        self.google_news_table = 'google_news_' + keyword.lower()
        cursor = self.db.cursor()
        colum_info = ",".join(col_name + ' ' + col_type for col_name, col_type in self.google_news_columns.items())
        query = "CREATE TABLE IF NOT EXISTS {} ({})".format(self.google_news_table, colum_info)
        cursor.execute(query)
        self.db.commit()

    def queryInsertGoogleNewsTable(self, values):
        cursor = self.db.cursor()
        colums = ','.join(self.google_news_columns.keys())
        values = '","'.join(str(values[col_name]).replace('"',"'") for col_name in self.google_news_columns.keys())
        query = 'INSERT OR IGNORE INTO {} ({}) VALUES ("{}")'.format(self.google_news_table, colums, values)
        cursor.execute(query)
        self.db.commit()

    def queryDeleteAllGoogleNewsTable(self, keyword):
        google_news_table = 'google_news_' + keyword.lower()
        query = "DROP TABLE IF EXISTS {}".format(google_news_table)
        cursor = self.db.cursor()
        cursor.execute(query)
        self.db.commit()

    def querySelectAllGoogleNewsTable(self, keyword):
        google_news_table = 'google_news_' + keyword.lower()
        query = "SELECT * FROM {}".format(google_news_table)
        cursor = self.db.cursor()
        cursor.execute(query)
        return cursor.fetchall()

    def queryCreateKeywordTable(self):
        cursor = self.db.cursor()
        colum_info = ",".join(col_name + ' ' + col_type for col_name, col_type in self.keyword_columns.items())
        query = "CREATE TABLE IF NOT EXISTS {} ({})".format(self.keyword_table, colum_info)
        cursor.execute(query)
        self.db.commit()

    def queryInsertKeywordTable(self, values):
        cursor = self.db.cursor()
        colums = ','.join(self.keyword_columns.keys())
        values = '","'.join(str(values[col_name]).replace('"',"'") for col_name in self.keyword_columns.keys())
        query = 'INSERT OR IGNORE INTO {} ({}) VALUES ("{}")'.format(self.keyword_table, colums, values)
        cursor.execute(query)
        self.db.commit()

    def queryDeleteKeywordTable(self, keyword):
        cursor = self.db.cursor()
        query = "DELETE FROM {} WHERE KEYWORD='{}'".format(self.keyword_table, keyword)
        cursor.execute(query)
        self.db.commit()

    def querySelectAllKeywordTable(self):
        query = "SELECT * FROM {}".format(self.keyword_table)
        cursor = self.db.cursor()
        cursor.execute(query)
        return cursor.fetchall()