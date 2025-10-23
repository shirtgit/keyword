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

def get_detailed_keyword_stats(keyword: str) -> list:
    """네이버 검색광고 API를 사용하여 키워드의 상세 통계 정보 추출"""
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
        
        # 결과 처리 - 상세 통계 포함
        detailed_keywords = []
        if 'keywordList' in result and result['keywordList']:
            for item in result['keywordList']:
                keyword_text = item.get('relKeyword', '').strip()
                if not keyword_text:
                    continue
                
                # 기본 통계 처리
                def process_stat(value):
                    """통계 값 처리 (문자열 및 특수 케이스 처리)"""
                    if isinstance(value, str):
                        if "< 10" in value:
                            return 5
                        elif "-" in value or value == "":
                            return 0
                    try:
                        return int(value) if value else 0
                    except (ValueError, TypeError):
                        return 0
                
                # PC 통계 - 안전한 처리
                pc_search = process_stat(item.get('monthlyPcQcCnt', 0))
                pc_click = process_stat(item.get('monthlyAvePcClkCnt', 0))
                
                # CTR 값 안전 처리
                try:
                    pc_ctr_raw = item.get('monthlyAvePcCtr', 0.0)
                    if isinstance(pc_ctr_raw, str):
                        pc_ctr = float(pc_ctr_raw) if pc_ctr_raw and pc_ctr_raw != '-' else 0.0
                    else:
                        pc_ctr = float(pc_ctr_raw) if pc_ctr_raw else 0.0
                except (ValueError, TypeError):
                    pc_ctr = 0.0
                
                pc_exposure = process_stat(item.get('plAvgDepth', 0))  # 광고 노출 수
                
                # 모바일 통계 - 안전한 처리
                mobile_search = process_stat(item.get('monthlyMobileQcCnt', 0))
                mobile_click = process_stat(item.get('monthlyAveMobileClkCnt', 0))
                
                # 모바일 CTR 값 안전 처리
                try:
                    mobile_ctr_raw = item.get('monthlyAveMobileCtr', 0.0)
                    if isinstance(mobile_ctr_raw, str):
                        mobile_ctr = float(mobile_ctr_raw) if mobile_ctr_raw and mobile_ctr_raw != '-' else 0.0
                    else:
                        mobile_ctr = float(mobile_ctr_raw) if mobile_ctr_raw else 0.0
                except (ValueError, TypeError):
                    mobile_ctr = 0.0
                
                mobile_exposure = process_stat(item.get('plAvgDepth', 0))  # 모바일도 동일한 필드 사용
                
                # 경쟁 정보 처리 개선
                competition_index = item.get('compIdx', 'N/A')
                
                # 경쟁도 처리 - 문자열과 숫자 모두 처리
                if competition_index != 'N/A' and competition_index is not None:
                    try:
                        # 이미 문자열인 경우 그대로 사용
                        if isinstance(competition_index, str):
                            if competition_index in ['낮음', '보통', '높음']:
                                competition_level = competition_index
                                # 문자열을 숫자로 역변환 (광고수 계산용)
                                if competition_index == '낮음':
                                    comp_idx_numeric = 20
                                elif competition_index == '보통':
                                    comp_idx_numeric = 50
                                else:  # '높음'
                                    comp_idx_numeric = 80
                            else:
                                # 숫자형 문자열인 경우
                                comp_idx_numeric = float(competition_index)
                                if comp_idx_numeric <= 30:
                                    competition_level = '낮음'
                                elif comp_idx_numeric <= 70:
                                    competition_level = '보통'
                                else:
                                    competition_level = '높음'
                        else:
                            # 숫자인 경우
                            comp_idx_numeric = float(competition_index)
                            if comp_idx_numeric <= 30:
                                competition_level = '낮음'
                            elif comp_idx_numeric <= 70:
                                competition_level = '보통'
                            else:
                                competition_level = '높음'
                    except (ValueError, TypeError):
                        competition_level = '알 수 없음'
                        comp_idx_numeric = 50  # 기본값
                else:
                    competition_level = '알 수 없음'
                    comp_idx_numeric = 50  # 기본값
                
                detailed_keywords.append({
                    'keyword': keyword_text,
                    # 월간 검색수
                    'monthly_pc_search': pc_search,
                    'monthly_mobile_search': mobile_search,
                    'total_monthly_search': pc_search + mobile_search,
                    
                    # 월평균 클릭수
                    'monthly_avg_pc_click': pc_click,
                    'monthly_avg_mobile_click': mobile_click,
                    'total_monthly_avg_click': pc_click + mobile_click,
                    
                    # 월평균 클릭률
                    'monthly_avg_pc_ctr': pc_ctr,
                    'monthly_avg_mobile_ctr': mobile_ctr,
                    'total_monthly_avg_ctr': (pc_ctr + mobile_ctr) / 2 if pc_ctr > 0 or mobile_ctr > 0 else 0,
                    
                    # 경쟁 정보
                    'competition_index': competition_index,
                    'competition_level': competition_level,
                    
                    # 노출 관련 (광고 깊이를 노출 수 대용으로 사용)
                    'pc_exposure': pc_exposure,
                    'mobile_exposure': mobile_exposure,
                    'total_exposure': pc_exposure + mobile_exposure,
                    
                    # 광고수 (경쟁도 기반 추정) - 안전한 처리
                    'estimated_ads_count': max(1, int(comp_idx_numeric / 10)),
                    
                    # 기타
                    'source': 'search_ads_api'
                })
        
        return detailed_keywords
        
    except Exception as e:
        st.error(f"❌ 검색광고 API 상세 분석 오류: {e}")
        return []

def get_related_keywords(keyword: str) -> list:
    """네이버 검색광고 API를 사용하여 연관 키워드 및 상세 통계 추출"""
    st.info("🎯 네이버 검색광고 API에서 상세 키워드 데이터 수집 중...")
    
    # 상세 통계 데이터 수집
    detailed_keywords = get_detailed_keyword_stats(keyword)
    
    if detailed_keywords:
        # 검색량 기준으로 정렬
        detailed_keywords.sort(key=lambda x: x.get('total_monthly_search', 0), reverse=True)
        st.success(f"🎉 총 {len(detailed_keywords)}개의 연관 키워드와 상세 통계를 발견했습니다!")
        return detailed_keywords
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