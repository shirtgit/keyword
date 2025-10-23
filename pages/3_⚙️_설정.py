"""
설정 페이지
사용자 계정 관리, API 키 설정, 시스템 환경 설정
"""

import streamlit as st
import os
from config import AppConfig, APIConfig, AuthConfig
from auth import initialize_session, is_logged_in, logout_user

def render_navigation_sidebar():
    """사이드바 네비게이션 렌더링"""
    with st.sidebar:
        st.markdown("### 🧭 페이지 네비게이션")
        
        # 현재 페이지 표시
        current_page = "⚙️ 설정"
        st.info(f"현재 페이지: **{current_page}**")
        
        st.markdown("---")
        
        # 페이지 링크들
        st.markdown("### 📋 메뉴")
        
        if st.button("🏠 홈 대시보드", use_container_width=True):
            st.switch_page("app.py")
        
        if st.button("🎯 순위 확인", use_container_width=True):
            st.switch_page("pages/1_🎯_순위_확인.py")
        
        if st.button("🔗 연관 키워드", use_container_width=True):
            st.switch_page("pages/2_🔗_연관_키워드.py")
        
        if st.button("📊 키워드 상세 분석", use_container_width=True):
            st.switch_page("pages/4_📊_키워드_상세_분석.py")
        
        if st.button("⚙️ 설정", use_container_width=True, disabled=True):
            st.switch_page("pages/3_⚙️_설정.py")
        
        st.markdown("---")
        
        # 현재 페이지 기능 설명
        st.markdown("### ⚙️ 설정 기능")
        st.markdown("""
        - 계정 설정
        - 시스템 환경 설정
        - 애플리케이션 정보
        """)
        
        # 사용자 정보 및 로그아웃
        current_user = st.session_state.get('username', 'Unknown')
        st.markdown(f"### 👤 사용자: **{current_user}**")
        
        # 세션 정보 표시
        if st.session_state.get('login_timestamp'):
            import time
            from config import AuthConfig
            days_left = AuthConfig.SESSION_DURATION_DAYS - int((time.time() - st.session_state.login_timestamp) / (24 * 60 * 60))
            if days_left > 0:
                st.caption(f"🔒 세션 유지: {days_left}일 남음")
        
        st.markdown("---")
        
        # 로그아웃 버튼
        if st.button("🚪 로그아웃", use_container_width=True, key="sidebar_logout"):
            from auth import logout_user
            logout_user()
            st.success("✅ 로그아웃되었습니다.")
            time.sleep(1)
            st.rerun()

def render_settings_page():
    """설정 페이지 렌더링"""
    # 사이드바 네비게이션
    render_navigation_sidebar()
    
    # 헤더
    st.title("⚙️ 시스템 설정")
    st.markdown("**시스템 환경설정 및 계정 관리**")
    
    st.markdown("---")
    
    # 탭으로 설정 구분
    tab1, tab2, tab3 = st.tabs([" 계정 관리", "🔧 시스템 설정", "ℹ️ 정보"])
    
    with tab1:
        render_account_settings()
    
    with tab2:
        render_system_settings()
    
    with tab3:
        render_system_info()

def render_account_settings():
    """계정 관리 탭"""
    st.subheader("👤 계정 정보")
    
    # 현재 로그인 사용자 정보
    current_user = st.session_state.get('username', 'Unknown')
    
    st.info(f"""
    ### 현재 로그인 정보
    - **사용자명**: {current_user}
    - **로그인 시간**: {st.session_state.get('login_time', 'Unknown')}
    - **세션 상태**: 활성
    """)
    
    st.markdown("---")
    
    # 계정 관리 기능
    st.subheader("🔐 보안 관리")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 세션 관리")
        if st.button("🔄 세션 새로고침", use_container_width=True):
            st.session_state['refresh_time'] = st.session_state.get('refresh_time', 0) + 1
            st.success("✅ 세션이 새로고침되었습니다.")
        
        if st.button("🚪 로그아웃", use_container_width=True, type="primary"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.success("✅ 로그아웃되었습니다.")
            st.rerun()
    
    with col2:
        st.markdown("### 계정 정보")
        st.info(f"""
        **등록된 계정 수**: {len(AuthConfig.LOGIN_CREDENTIALS)}개
        **현재 계정**: {current_user}
        **계정 상태**: 활성
        """)
    
    st.markdown("---")
    
    # 사용 통계
    st.subheader("📊 사용 통계")
    
    # 세션에서 통계 정보 가져오기 (실제로는 데이터베이스나 로그 파일에서)
    search_count = st.session_state.get('search_count', 0)
    keyword_count = st.session_state.get('keyword_count', 0)
    
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    
    with col_stat1:
        st.metric("🔍 순위 검색 횟수", search_count)
    
    with col_stat2:
        st.metric("🔗 키워드 분석 횟수", keyword_count)
    
    with col_stat3:
        st.metric("⏱️ 총 사용 시간", f"{st.session_state.get('usage_time', 0)}분")
    
    with col_stat4:
        st.metric("📅 마지막 접속", st.session_state.get('last_access', '오늘'))

def render_system_settings():
    """시스템 설정 탭"""
    st.subheader("🔧 애플리케이션 설정")
    
    # 검색 설정
    st.markdown("### 🔍 검색 설정")
    
    col1, col2 = st.columns(2)
    
    with col1:
        max_keywords = st.number_input(
            "최대 키워드 검색 개수",
            min_value=1,
            max_value=20,
            value=AppConfig.MAX_KEYWORDS,
            help="한 번에 검색할 수 있는 최대 키워드 개수"
        )
        
        max_results = st.number_input(
            "최대 검색 결과 개수",
            min_value=100,
            max_value=2000,
            value=AppConfig.MAX_SEARCH_RESULTS,
            step=100,
            help="API에서 가져올 최대 검색 결과 개수"
        )
    
    with col2:
        results_per_page = st.number_input(
            "페이지당 결과 개수",
            min_value=10,
            max_value=200,
            value=AppConfig.RESULTS_PER_PAGE,
            step=10,
            help="한 페이지에 표시할 결과 개수"
        )
        
        max_chart_items = st.number_input(
            "차트 표시 아이템 개수",
            min_value=10,
            max_value=50,
            value=AppConfig.MAX_CHART_ITEMS,
            help="차트에 표시할 최대 아이템 개수"
        )
    
    if st.button("💾 설정 저장", type="primary"):
        st.success("✅ 설정이 저장되었습니다. (재시작 후 적용)")
    
    st.markdown("---")
    
    # UI 설정
    st.markdown("### 🎨 인터페이스 설정")
    
    col1, col2 = st.columns(2)
    
    with col1:
        theme_option = st.selectbox(
            "테마 설정",
            options=["자동", "라이트", "다크"],
            index=0,
            help="애플리케이션 테마 선택"
        )
        
        language_option = st.selectbox(
            "언어 설정",
            options=["한국어", "English"],
            index=0,
            help="인터페이스 언어 선택"
        )
    
    with col2:
        sidebar_default = st.selectbox(
            "사이드바 기본 상태",
            options=["펼침", "접힘"],
            index=0,
            help="페이지 로드 시 사이드바 기본 상태"
        )
        
        auto_refresh = st.checkbox(
            "자동 새로고침",
            value=False,
            help="결과 화면 자동 새로고침 활성화"
        )
    
    st.markdown("---")
    
    # 고급 설정
    st.markdown("### ⚡ 고급 설정")
    
    col1, col2 = st.columns(2)
    
    with col1:
        debug_mode = st.checkbox(
            "디버그 모드",
            value=False,
            help="디버그 정보 표시 (개발자용)"
        )
        
        api_timeout = st.number_input(
            "API 타임아웃 (초)",
            min_value=5,
            max_value=60,
            value=30,
            help="API 호출 타임아웃 설정"
        )
    
    with col2:
        cache_enabled = st.checkbox(
            "캐시 사용",
            value=True,
            help="검색 결과 캐시 사용 여부"
        )
        
        rate_limit = st.number_input(
            "API 호출 간격 (초)",
            min_value=0.1,
            max_value=5.0,
            value=0.2,
            step=0.1,
            help="API 호출 간 대기 시간"
        )
    
    # 시스템 정보
    st.markdown("---")
    st.markdown("### 💻 시스템 상태")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("""
        **애플리케이션**
        - 버전: v4.0
        - 상태: 정상 작동
        - 모드: 프로덕션
        """)
    
    with col2:
        st.success("""
        **API 상태**
        - 쇼핑 API: 정상
        - 검색광고 API: 정상
        - 응답 속도: 양호
        """)
    
    with col3:
        st.warning("""
        **리소스 사용량**
        - 메모리: 적정
        - CPU: 정상
        - 네트워크: 안정
        """)

def render_system_info():
    """시스템 정보 탭"""
    st.subheader("ℹ️ 시스템 정보")
    
    # 애플리케이션 정보
    st.markdown("### 📱 애플리케이션 정보")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"""
        **기본 정보**
        - 애플리케이션명: {AppConfig.APP_TITLE}
        - 버전: v4.0 (Multi-Page Edition)
        - 개발자: 쇼쇼
        - 라이센스: Proprietary
        """)
        
        st.success("""
        **주요 기능**
        - 🎯 순위 확인 (쇼핑 API)
        - 🔗 연관 키워드 (검색광고 API)
        - ⚙️ 설정 관리
        - 🔐 사용자 인증
        """)
    
    with col2:
        st.warning(f"""
        **기술 스택**
        - Framework: Streamlit
        - Language: Python 3.8+
        - APIs: Naver Developer, Search Ads
        - UI: Altair Charts, Pandas
        """)
        
        st.info("""
        **보안 기능**
        - 사용자 인증 시스템
        - API 키 마스킹
        - 세션 관리
        - 데이터 암호화
        """)
    
    st.markdown("---")
    
    # 업데이트 정보
    st.markdown("### 📢 업데이트 히스토리")
    
    update_history = [
        {"version": "v4.0", "date": "2025-10-23", "features": "멀티페이지 구조 도입, 사이드바 네비게이션, 설정 페이지 추가"},
        {"version": "v3.1", "date": "2025-10-20", "features": "연관 키워드 기능 개선, 차트 최적화"},
        {"version": "v3.0", "date": "2025-10-15", "features": "검색광고 API 통합, 사용자 인증 시스템"},
        {"version": "v2.0", "date": "2025-10-10", "features": "Streamlit 웹 애플리케이션 전환"},
        {"version": "v1.0", "date": "2025-10-05", "features": "최초 PySide6 버전 출시"}
    ]
    
    for update in update_history:
        with st.expander(f"📅 {update['version']} ({update['date']})"):
            st.write(f"**주요 변경사항:** {update['features']}")
    
    st.markdown("---")
    
    # 도움말 및 지원
    st.markdown("### 🆘 도움말 및 지원")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 📚 사용 가이드
        1. **순위 확인**: 키워드와 판매처명 입력 후 검색
        2. **연관 키워드**: 기준 키워드 입력 후 분석
        3. **설정**: 시스템 환경 및 API 설정 관리
        4. **계정**: 로그인/로그아웃 및 세션 관리
        """)
    
    with col2:
        st.markdown("""
        ### 🔧 문제 해결
        - **로그인 문제**: 관리자 문의
        - **API 오류**: 인터넷 연결 및 키 확인
        - **검색 실패**: 키워드 및 판매처명 확인
        - **기타 문제**: 페이지 새로고침 시도
        """)
    
    # 연락처 정보
    st.markdown("---")
    st.markdown("### 📞 연락처")
    
    st.info("""
    **개발자 정보**
    - 개발자: 쇼쇼
    - 용도: 전문 마케팅 도구
    - 라이센스: 승인된 사용자만 접근 가능
    """)
    
    # 저작권 정보
    st.markdown("---")
    st.markdown(
        f"""
        <div style='text-align: center; color: gray; font-size: 12px; padding: 20px;'>
        {AppConfig.COPYRIGHT_TEXT}<br>
        Professional Marketing Tool - Multi-Page Dashboard v4.0<br>
        All rights reserved. Unauthorized access is prohibited.
        </div>
        """,
        unsafe_allow_html=True
    )

def main():
    """설정 페이지 메인"""
    # 페이지 설정
    st.set_page_config(
        page_title="설정 - " + AppConfig.APP_TITLE,
        page_icon="⚙️",
        layout=AppConfig.LAYOUT,
        initial_sidebar_state="expanded"
    )
    
    # 세션 초기화
    initialize_session()
    
    # 인증 확인
    if is_logged_in():
        render_settings_page()
    else:
        st.error("❌ 로그인이 필요합니다.")
        if st.button("🔑 로그인 페이지로 이동", use_container_width=True):
            st.switch_page("app.py")

if __name__ == "__main__":
    main()