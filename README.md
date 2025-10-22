# 네이버 쇼핑 분석기 (by 쇼쇼)

네이버 쇼핑에서 상품 순위 확인과 연관 키워드 분석을 제공하는 Streamlit 웹 애플리케이션입니다.

## 🔍 주요 기능

### 📊 순위 확인
- 네이버 쇼핑에서 특정 판매처의 상품 순위 검색
- 여러 키워드 동시 검색 (최대 10개)
- 실시간 검색 진행 상황 표시
- 순위별 정렬된 결과 제공

### 🔗 연관 키워드 분석
- 기준 키워드의 연관 키워드 추출 (무제한)
- 최대 1,000개 상품 데이터 분석
- 빈도 및 연관도 분석
- 시각적 차트 및 데이터 표시
- CSV 다운로드 기능

## 🚀 설치 및 실행

### 1. 환경 설정

```bash
# 저장소 클론
git clone https://github.com/shirtgit/keyword.git
cd keyword

# Python 패키지 설치
pip install -r requirements.txt
```

### 2. API 키 설정

1. `.env.example` 파일을 `.env`로 복사
2. 네이버 개발자센터에서 API 키 발급
3. `.env` 파일에 실제 API 키 입력

```bash
# .env 파일 생성
cp .env.example .env
```

`.env` 파일 내용:
```
NAVER_CLIENT_ID=your_actual_client_id
NAVER_CLIENT_SECRET=your_actual_client_secret
```

### 3. 실행

```bash
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 접속

## 📋 필수 요구사항

- Python 3.7+
- 네이버 개발자 API 키
- 인터넷 연결

## 🔒 보안 주의사항

- `.env` 파일은 절대 Git에 커밋하지 마세요
- API 키는 안전한 곳에 보관하세요
- 공개 저장소에 민감한 정보를 업로드하지 마세요

## 📞 지원

문의사항이 있으시면 이슈를 등록해주세요.

---
ⓒ 2025 쇼쇼. All rights reserved.
