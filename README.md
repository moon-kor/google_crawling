# Google News 크롤링 시스템

Google News RSS 피드를 활용하여 뉴스를 자동으로 수집하고 SQLite 데이터베이스에 저장하는 Python 스크립트입니다.

## 🚀 주요 기능

- **Google News RSS 크롤링**: 키워드 기반 뉴스 수집
- **다국가 지원**: 한국(ko) 및 영어권(en) 뉴스 수집
- **자동 스케줄링**: APScheduler를 이용한 자동 실행
- **데이터베이스 관리**: SQLite를 이용한 뉴스 데이터 저장
- **중복 방지**: 동일한 뉴스 중복 수집 방지

## 📁 파일 구조

```
구글뉴스크롤링/
├── main.py                    # 데이터베이스 관리 클래스
├── google_news_dbmanager.py   # 데이터베이스 관리자 (main.py와 동일)
├── google_news_cron.py        # Google News 크롤링 및 스케줄링
├── simple_search.py           # 명령줄 기반 간단 검색
├── interactive_search.py      # 인터랙티브 검색 인터페이스
├── multi_keyword_test.py      # 여러 키워드 일괄 검색
├── test_run.py               # 기본 테스트 스크립트
├── debug_test.py             # 디버깅용 테스트 스크립트
├── google_news.db            # SQLite 데이터베이스 파일
└── README.md                 # 프로젝트 설명서
```

## 🛠️ 설치 및 설정

### 1. 필요한 라이브러리 설치

```bash
pip install apscheduler requests maya feedparser
```

### 2. 프로젝트 클론

```bash
git clone https://github.com/moon-kor/google_crawling.git
cd google_crawling
```

## 📖 사용법

### 1. 간단한 명령줄 검색

```bash
# 한국 뉴스 검색
python simple_search.py "키워드" ko

# 영어권 뉴스 검색
python simple_search.py "키워드" en

# 예시
python simple_search.py "삼성전자" ko
python simple_search.py "Apple" en
python simple_search.py "Tesla" en
```

### 2. 인터랙티브 검색

```bash
python interactive_search.py
```

키워드와 국가를 직접 입력하여 검색할 수 있습니다.

### 3. 여러 키워드 일괄 검색

```bash
python multi_keyword_test.py
```

미리 설정된 키워드들로 한 번에 검색합니다.

### 4. 스케줄링 실행

```python
from google_news_cron import GoogleNewsCron

cron = GoogleNewsCron()

# 한 번만 실행
cron.run(mode='once', country='ko', keyword='삼성전자')

# 10초마다 반복 실행
cron.run(mode='interval', country='ko', keyword='삼성전자')

# Cron 방식으로 10초마다 실행
cron.run(mode='cron', country='ko', keyword='삼성전자')
```

## 🗄️ 데이터베이스 구조

### 뉴스 테이블 (`google_news_키워드명`)
- `published`: 발행일시 (text)
- `source`: 뉴스 출처 (text, PRIMARY KEY)
- `title`: 뉴스 제목 (text)
- `link`: 뉴스 링크 (text)

### 키워드 테이블 (`keyword`)
- `keyword`: 검색 키워드 (text, PRIMARY KEY)
- `country`: 국가 코드 (text)

## 🔧 주요 클래스 및 메서드

### GoogleNewsDBManager
- `queryCreateGoogleNewsTable(keyword)`: 키워드별 뉴스 테이블 생성
- `queryInsertGoogleNewsTable(values)`: 뉴스 데이터 삽입
- `querySelectAllGoogleNewsTable(keyword)`: 키워드별 뉴스 조회
- `queryDeleteAllGoogleNewsTable(keyword)`: 키워드별 뉴스 테이블 삭제

### GoogleNewsCron
- `run(mode, country, keyword)`: 크롤링 실행
- `stop()`: 스케줄러 중지

## 📊 실행 예시

### 성공적인 크롤링 결과

```
=== '삼성전자' 키워드로 한국 뉴스 검색 ===
총 25개의 뉴스가 수집되었습니다.

수집된 뉴스:
1. 삼성전자, 재생에너지 사용량 1만GWh 넘겨...애플, 구글과 어깨 나란히
   출처: M이코노미뉴스
   날짜: 2025-06-28 17:22:19

2. 삼성전자, 해외 직원 1만명 감축···국내 12만5천명 '역대 최대'
   출처: 이뉴스투데이
   날짜: 2025-06-28 16:44:18
```

## ⚠️ 주의사항

1. **Google News 정책 준수**: 과도한 요청으로 인한 차단을 방지하기 위해 적절한 간격을 두고 사용하세요.
2. **데이터베이스 백업**: 중요한 데이터는 정기적으로 백업하세요.
3. **네트워크 연결**: 인터넷 연결이 필요합니다.

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📞 문의

프로젝트에 대한 문의사항이 있으시면 [GitHub Issues](https://github.com/moon-kor/google_crawling/issues)를 통해 연락해주세요.
