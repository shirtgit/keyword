"""
Configuration file for the marketing tool
환경 변수 및 설정 정보 중앙 관리
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API 설정
class APIConfig:
    """API 관련 설정"""
    
    # 네이버 개발자 API (쇼핑 API)
    NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID", "RMAReoKGgZ73JCL3AdhK")
    NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET", "SZS7VRIQDT")
    
    # 네이버 검색광고 API
    CUSTOMER_ID = os.getenv("CUSTOMER_ID")
    ACCESS_LICENSE = os.getenv("ACCESS_LICENSE")
    SECRET_KEY = os.getenv("SECRET_KEY")
    
    # Google Gemini API
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyAMMcJt93wdo8FNY22MGQrvl9o4BiF10-c")
    
    # API URLs
    NAVER_SHOPPING_API_URL = "https://openapi.naver.com/v1/search/shop.json"
    NAVER_ADS_API_BASE_URL = "https://api.naver.com"
    NAVER_ADS_API_PATH = "/keywordstool"

# 인증 설정
class AuthConfig:
    """인증 관련 설정"""
    
    LOGIN_CREDENTIALS = {
        "hyehye": "h2t12345"
    }
    
    # 세션 관리
    SESSION_SECRET = "marketing_tool_secret_key_2025"
    SESSION_DURATION_DAYS = 7  # 세션 유지 기간 (일)

# 애플리케이션 설정
class AppConfig:
    """애플리케이션 기본 설정"""
    
    APP_TITLE = "마케팅 도구 (by 쇼쇼)"
    APP_ICON = "🔍"
    LAYOUT = "wide"
    
    # 검색 설정
    MAX_KEYWORDS = 10
    MAX_SEARCH_RESULTS = 1000
    RESULTS_PER_PAGE = 100
    
    # 차트 설정
    MAX_CHART_ITEMS = 20
    
    # 기타 설정
    COPYRIGHT_TEXT = "ⓒ 2025 쇼쇼. 무단 복제 및 배포 금지. All rights reserved."

# 디버그 설정
class DebugConfig:
    """디버그 관련 설정"""
    
    SHOW_DEBUG_INFO = True
    LOG_API_RESPONSES = True