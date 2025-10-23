"""
API module for the marketing tool
네이버 쇼핑 API 및 검색광고 API 관련 기능
"""

import json
import urllib.request
import urllib.parse
import re
import time
import hashlib
import hmac
import base64
from collections import Counter
import streamlit as st
from config import APIConfig, AppConfig, DebugConfig

def get_signature(method: str, uri: str, timestamp: str, access_key: str, secret_key: str) -> str:
    """네이버 검색광고 API 인증을 위한 서명 생성"""
    message = f"{timestamp}.{method}.{uri}"
    signature = base64.b64encode(
        hmac.new(secret_key.encode(), message.encode(), hashlib.sha256).digest()
    ).decode()
    return signature

def get_related_keywords_from_ads_api(keyword: str) -> list:
    """네이버 검색광고 API를 사용하여 연관 키워드 추출"""
    try:
        # 인증 정보 확인
        if not all([APIConfig.ACCESS_LICENSE, APIConfig.SECRET_KEY, APIConfig.CUSTOMER_ID]):
            st.error("❌ 네이버 검색광고 API 설정이 필요합니다.")
            return []
        
        # 타임스탬프 생성
        timestamp = str(int(time.time() * 1000))
        
        # 서명 생성
        signature = get_signature("GET", APIConfig.NAVER_ADS_API_PATH, timestamp, 
                                 APIConfig.ACCESS_LICENSE, APIConfig.SECRET_KEY)
        
        # 헤더 설정
        headers = {
            "X-Timestamp": timestamp,
            "X-API-KEY": APIConfig.ACCESS_LICENSE,
            "X-Customer": APIConfig.CUSTOMER_ID,
            "X-Signature": signature,
            "Content-Type": "application/json"
        }
        
        # GET 방식으로 쿼리 파라미터 전송
        query_params = urllib.parse.urlencode({
            'hintKeywords': keyword,
            'showDetail': '1'
        })
        url = f"{APIConfig.NAVER_ADS_API_BASE_URL}{APIConfig.NAVER_ADS_API_PATH}?{query_params}"
        request = urllib.request.Request(url, headers=headers, method="GET")
        
        with urllib.request.urlopen(request) as response:
            response_data = response.read()
            result = json.loads(response_data.decode('utf-8'))
            
        # 디버깅 정보 표시
        if DebugConfig.SHOW_DEBUG_INFO:
            st.write(f"API 응답 상태: OK")
            if 'keywordList' in result:
                st.write(f"API에서 받은 키워드 수: {len(result['keywordList'])}")
            else:
                st.write(f"API 응답 구조: {list(result.keys())}")
                
        # 결과 처리
        related_keywords = []
        if 'keywordList' in result and result['keywordList']:
            for item in result['keywordList']:
                # 키워드가 비어있지 않은지 확인
                keyword_text = item.get('relKeyword', '').strip()
                if not keyword_text:
                    continue
                    
                # 검색량 처리
                pc_qc = item.get('monthlyPcQcCnt', 0)
                mobile_qc = item.get('monthlyMobileQcCnt', 0)
                
                # "< 10" 같은 문자열 처리
                if isinstance(pc_qc, str):
                    pc_qc = 5 if "< 10" in pc_qc else 0
                if isinstance(mobile_qc, str):
                    mobile_qc = 5 if "< 10" in mobile_qc else 0
                
                # 숫자가 아닌 경우 0으로 처리
                try:
                    pc_qc = int(pc_qc) if pc_qc else 0
                    mobile_qc = int(mobile_qc) if mobile_qc else 0
                except (ValueError, TypeError):
                    pc_qc = 0
                    mobile_qc = 0
                
                related_keywords.append({
                    'keyword': keyword_text,
                    'monthly_pc_qc': pc_qc,
                    'monthly_mobile_qc': mobile_qc,
                    'competition': item.get('compIdx', 'N/A'),
                    'source': 'ads_api'
                })
        
        if DebugConfig.SHOW_DEBUG_INFO:
            st.write(f"처리된 키워드 수: {len(related_keywords)}")
        
        return related_keywords
        
    except Exception as e:
        st.error(f"❌ 검색광고 API 오류: {e}")
        return []

def get_related_keywords(keyword: str) -> list:
    """네이버 검색광고 API를 사용하여 연관 키워드 추출"""
    st.info("🎯 네이버 검색광고 API에서 연관 키워드 수집 중...")
    related_keywords = get_related_keywords_from_ads_api(keyword)
    
    if related_keywords:
        # 검색량 기준으로 정렬
        related_keywords.sort(key=lambda x: (x.get('monthly_pc_qc', 0) + x.get('monthly_mobile_qc', 0)), reverse=True)
        st.success(f"🎉 총 {len(related_keywords)}개의 연관 키워드를 발견했습니다!")
        return related_keywords
    else:
        st.error("❌ 연관 키워드를 찾을 수 없습니다.")
        return []

def get_top_ranked_product_by_mall(keyword: str, mall_name: str) -> dict:
    """네이버 쇼핑에서 특정 키워드로 검색하여 지정된 판매처의 최고 순위 상품을 찾는 함수"""
    encText = urllib.parse.quote(keyword)
    seen_titles = set()
    best_product = None
    
    for start in range(1, AppConfig.MAX_SEARCH_RESULTS + 1, AppConfig.RESULTS_PER_PAGE):
        url = f"{APIConfig.NAVER_SHOPPING_API_URL}?query={encText}&display={AppConfig.RESULTS_PER_PAGE}&start={start}"
        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", APIConfig.NAVER_CLIENT_ID)
        request.add_header("X-Naver-Client-Secret", APIConfig.NAVER_CLIENT_SECRET)
        
        try:
            response = urllib.request.urlopen(request)
            result = json.loads(response.read())
            
            for idx, item in enumerate(result.get("items", []), start=1):
                if item.get("mallName") and mall_name in item["mallName"]:
                    title_clean = re.sub(r"<.*?>", "", item["title"])
                    if title_clean in seen_titles:
                        continue
                    seen_titles.add(title_clean)
                    
                    rank = start + idx - 1
                    product = {
                        "rank": rank,
                        "title": title_clean,
                        "price": item["lprice"],
                        "link": item["link"],
                        "mallName": item["mallName"]
                    }
                    
                    if not best_product or rank < best_product["rank"]:
                        best_product = product
        except Exception as e:
            st.error(f"API 요청 중 오류가 발생했습니다: {e}")
            break
    
    return best_product