"""
네이버 마케팅 분석기 - 메인 애플리케이션
쇼쇼의 전문 마케팅 도구
"""

import streamlit as st
from config import AppConfig
from auth import initialize_session, is_logged_in, render_login_page, render_logout_section

def render_navigation_sidebar():
    """사이드바 네비게이션 렌더링"""
    with st.sidebar:
        st.markdown("### 🧭 페이지 네비게이션")
        
        # 현재 페이지 표시
        current_page = "🏠 홈 대시보드"
        st.info(f"현재 페이지: **{current_page}**")
        
        st.markdown("---")
        
        # 페이지 링크들
        st.markdown("### 📋 메뉴")
        
        if st.button("🏠 홈 대시보드", use_container_width=True, disabled=True):
            st.switch_page("app.py")
        
        if st.button("🎯 순위 확인", use_container_width=True):
            st.switch_page("pages/1_🎯_순위_확인.py")
        
        if st.button("🔗 연관 키워드", use_container_width=True):
            st.switch_page("pages/2_🔗_연관_키워드.py")
        
        if st.button("📊 키워드 상세 분석", use_container_width=True):
            st.switch_page("pages/4_📊_키워드_상세_분석.py")
        
        if st.button("⚙️ 설정", use_container_width=True):
            st.switch_page("pages/3_⚙️_설정.py")
        
        st.markdown("---")
        
        # 퀵 액세스
        st.markdown("### ⚡ 퀵 액세스")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔍", help="순위 확인 바로가기"):
                st.switch_page("pages/1_🎯_순위_확인.py")
        with col2:
            if st.button("📊", help="키워드 분석 바로가기"):
                st.switch_page("pages/2_🔗_연관_키워드.py")
        
        st.markdown("---")
        
        # 시스템 상태
        st.markdown("### 🔧 시스템 상태")
        st.success("🟢 모든 시스템 정상")
        st.info("📡 API 연결 안정")
        
        # 사용자 정보
        current_user = st.session_state.get('username', 'Unknown')
        st.markdown(f"### 👤 사용자: **{current_user}**")

def render_dashboard_overview():
    """대시보드 개요 렌더링"""
    # 다크모드/라이트모드 대응 CSS
    st.markdown("""
    <style>
    /* 컨테이너 최적화 */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 1200px;
    }
    
    /* 헤더 스타일 - 고정 색상으로 가독성 보장 */
    .main-header {
        background: linear-gradient(135deg, #20B2AA, #48D1CC);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(32, 178, 170, 0.3);
    }
    
    .main-title {
        color: white !important;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .main-subtitle {
        color: rgba(255,255,255,0.9) !important;
        font-size: 1rem;
        margin: 0.5rem 0 0 0;
        font-weight: 400;
    }
    
    /* 카드 스타일 - 시스템 테마 대응 */
    .feature-card {
        background: var(--background-color, white);
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.1);
        border: 1px solid rgba(32, 178, 170, 0.2);
        height: 100%;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        margin-bottom: 1rem;
    }
    
    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(32, 178, 170, 0.2);
    }
    
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        display: block;
    }
    
    .feature-title {
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 0.8rem;
        color: #20B2AA;
    }
    
    .feature-desc {
        font-size: 0.95rem;
        line-height: 1.5;
        margin-bottom: 1.2rem;
        opacity: 0.8;
    }
    
    /* 버튼 스타일 - 고정 색상 */
    .stButton > button {
        background: linear-gradient(135deg, #20B2AA, #48D1CC) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
        box-shadow: 0 2px 6px rgba(32, 178, 170, 0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #48D1CC, #40E0D0) !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 10px rgba(32, 178, 170, 0.4);
    }
    
    /* 여백 최적화 */
    .element-container {
        margin-bottom: 0.5rem;
    }
    
    .row-widget {
        padding: 0.2rem 0;
    }
    
    /* 컬럼 간격 조정 */
    .column {
        padding: 0 0.5rem;
    }
    
    /* 메트릭 카드 최적화 */
    [data-testid="metric-container"] {
        border: 1px solid rgba(32, 178, 170, 0.2);
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.5rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 사이드바 네비게이션
    render_navigation_sidebar()
    
    # 헤더
    st.markdown("""
    <div class="main-header">
        <h1 class="main-title">🏠 네이버 마케팅 분석기</h1>
        <p class="main-subtitle">by 쇼쇼 | 현대적이고 심플한 마케팅 도구</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 로그아웃 섹션을 우상단에 배치
    col_spacer, col_logout = st.columns([4, 1])
    with col_logout:
        render_logout_section()
    
    # 심플한 기능 카드
    col1, col2, col3 = st.columns(3, gap="large")
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">🎯</span>
            <h3 class="feature-title">순위 확인</h3>
            <p class="feature-desc">네이버 쇼핑에서 키워드별 판매처 순위를 실시간으로 확인하세요</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("시작하기", key="rank_btn", use_container_width=True):
            st.switch_page("pages/1_🎯_순위_확인.py")
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">🔗</span>
            <h3 class="feature-title">연관 키워드</h3>
            <p class="feature-desc">키워드 분석으로 검색량과 경쟁도를 파악하여 마케팅 전략을 세워보세요</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("시작하기", key="keyword_btn", use_container_width=True):
            st.switch_page("pages/2_🔗_연관_키워드.py")
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">📊</span>
            <h3 class="feature-title">상세 분석</h3>
            <p class="feature-desc">월간검색수, 클릭률, 경쟁정도 등 상세한 키워드 데이터를 분석하세요</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("시작하기", key="detail_btn", use_container_width=True):
            st.switch_page("pages/4_📊_키워드_상세_분석.py")
    


def main():
    """메인 애플리케이션"""
    # 페이지 설정
    st.set_page_config(
        page_title=AppConfig.APP_TITLE,
        page_icon=AppConfig.APP_ICON,
        layout=AppConfig.LAYOUT,
        initial_sidebar_state="expanded"  # 사이드바 기본 확장
    )
    
    # 세션 초기화
    initialize_session()
    
    # 인증 확인
    if is_logged_in():
        render_dashboard_overview()
        
        # 푸터
        st.markdown("---")
        st.markdown(
            f"""
            <div style='text-align: center; color: gray; font-size: 12px;'>
            {AppConfig.COPYRIGHT_TEXT}<br>
            Professional Marketing Tool - Authorized User Only<br>
            Multi-Page Dashboard v4.0
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        render_login_page()

if __name__ == "__main__":
    main()
