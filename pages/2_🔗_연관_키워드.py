"""
연관 키워드 페이지
네이버 검색광고 API를 활용한 키워드 분석 및 연관 키워드 발굴
"""

import streamlit as st
import pandas as pd
import altair as alt
import time
from api import get_related_keywords
from config import AppConfig, AuthConfig
from auth import initialize_session, is_logged_in, logout_user

def render_navigation_sidebar():
    """사이드바 네비게이션 렌더링"""
    with st.sidebar:
        st.markdown("### 🧭 페이지 네비게이션")
        
        # 현재 페이지 표시
        current_page = "🔗 연관 키워드"
        st.info(f"현재 페이지: **{current_page}**")
        
        st.markdown("---")
        
        # 페이지 링크들
        st.markdown("### 📋 메뉴")
        
        if st.button("🏠 홈 대시보드", use_container_width=True):
            st.switch_page("app.py")
        
        if st.button("🎯 순위 확인", use_container_width=True):
            st.switch_page("pages/1_🎯_순위_확인.py")
        
        if st.button("🔗 연관 키워드", use_container_width=True, disabled=True):
            st.switch_page("pages/2_🔗_연관_키워드.py")
        
        if st.button("📊 키워드 상세 분석", use_container_width=True):
            st.switch_page("pages/4_📊_키워드_상세_분석.py")
        
        if st.button("✍️ 글 재작성", use_container_width=True):
            st.switch_page("pages/5_✍️_글_재작성.py")
        
        if st.button("⚙️ 설정", use_container_width=True):
            st.switch_page("pages/3_⚙️_설정.py")
        
        st.markdown("---")
        
        # 현재 페이지 기능 설명
        st.markdown("### 🔗 연관 키워드 기능")
        st.markdown("""
        - 네이버 검색광고 API 활용
        - 연관 키워드 분석
        - 검색량 및 경쟁도 확인
        - 차트 및 CSV 다운로드
        """)
        
        # 사용자 정보 및 로그아웃
        current_user = st.session_state.get('username', 'Unknown')
        st.markdown(f"### 👤 사용자: **{current_user}**")
        
        # 세션 정보 표시
        if st.session_state.get('login_timestamp'):
            days_left = AuthConfig.SESSION_DURATION_DAYS - int((time.time() - st.session_state.login_timestamp) / (24 * 60 * 60))
            if days_left > 0:
                st.caption(f"🔒 세션 유지: {days_left}일 남음")
        
        st.markdown("---")
        
        # 로그아웃 버튼
        if st.button("🚪 로그아웃", use_container_width=True, key="sidebar_logout"):
            logout_user()
            st.success("✅ 로그아웃되었습니다.")
            time.sleep(1)
            st.rerun()

def render_related_keywords_page():
    """연관 키워드 페이지 렌더링"""
    # 민트 테마 CSS 적용
    st.markdown("""
    <style>
    .main .block-container { padding-top: 2rem; max-width: 1200px; }
    :root {
        --mint-primary: #40E0D0; --mint-secondary: #48D1CC; --mint-light: #AFEEEE;
        --mint-dark: #20B2AA; --mint-gradient: linear-gradient(135deg, #20B2AA, #48D1CC);
    }
    .page-header { background: var(--mint-gradient); color: white; padding: 2rem; border-radius: 15px; margin-bottom: 2rem; text-align: center; box-shadow: 0 4px 20px rgba(32, 178, 170, 0.3); }
    .page-title { font-size: 2.5rem; font-weight: 700; margin: 0; text-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .page-subtitle { font-size: 1.1rem; margin: 0.5rem 0 0 0; opacity: 0.9; }
    .stButton > button { background: var(--mint-gradient) !important; color: white !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; }
    .stButton > button:hover { background: linear-gradient(135deg, #48D1CC, #40E0D0) !important; transform: translateY(-1px) !important; }
    .metric-card { background: white; border-radius: 12px; padding: 1.5rem; box-shadow: 0 2px 12px rgba(0,0,0,0.1); border-left: 4px solid var(--mint-primary); margin-bottom: 1rem; }
    .keyword-item { background: rgba(64, 224, 208, 0.1); border-radius: 8px; padding: 1rem; margin: 0.5rem 0; border-left: 3px solid var(--mint-primary); }
    .download-section { background: rgba(32, 178, 170, 0.1); border-radius: 10px; padding: 1.5rem; margin: 1rem 0; border: 1px solid rgba(32, 178, 170, 0.3); }
    .chart-container { background: white; border-radius: 12px; padding: 1.5rem; box-shadow: 0 2px 12px rgba(0,0,0,0.1); }
    </style>""", unsafe_allow_html=True)
    
    # 사이드바 네비게이션
    render_navigation_sidebar()
    
    # 페이지 헤더
    st.markdown("""
    <div class="page-header">
        <h1 class="page-title">🔗 연관 키워드</h1>
        <p class="page-subtitle">키워드 분석으로 마케팅 전략을 최적화하세요</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 메인 입력 영역
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # 키워드 입력
        keyword_input = st.text_input(
            "🔍 기본 키워드 입력",
            placeholder="예: 노트북, 스마트폰, 화장품",
            help="분석하고자 하는 기본 키워드를 입력하세요"
        )
    
    with col2:
        # 검색 설정
        st.markdown("### ⚙️ 검색 설정")
        
        # 결과 개수 선택
        result_count = st.selectbox(
            "결과 개수",
            [10, 20, 30, 50],
            index=1,
            help="가져올 연관 키워드 개수"
        )
        
        # 정렬 기준
        sort_by = st.selectbox(
            "정렬 기준",
            ["검색량", "경쟁도", "키워드명"],
            help="결과 정렬 기준 선택"
        )
    
    # 검색 버튼
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        search_clicked = st.button("🚀 연관 키워드 분석 시작", use_container_width=True)
    
    if search_clicked and keyword_input:
        with st.spinner("🔍 연관 키워드를 검색하고 있습니다..."):
            # 연관 키워드 검색
            keywords_data = get_related_keywords(keyword_input.strip())
            
            if keywords_data and len(keywords_data) > 0:
                # 결과를 DataFrame으로 변환
                df = pd.DataFrame(keywords_data)
                
                # 결과 개수 제한
                df = df.head(result_count)
                
                # 정렬 (안전하게 처리)
                if sort_by == "검색량" and 'monthlyPcQcCnt' in df.columns:
                    df = df.sort_values('monthlyPcQcCnt', ascending=False)
                elif sort_by == "경쟁도" and 'compIdx' in df.columns:
                    df = df.sort_values('compIdx', ascending=False)
                elif 'relKeyword' in df.columns:  # 키워드명
                    df = df.sort_values('relKeyword')
                else:
                    # 기본적으로 첫 번째 컬럼으로 정렬
                    df = df.sort_values(df.columns[0])
                
                # 결과 저장 (세션 상태)
                st.session_state.keywords_result = df
                st.session_state.base_keyword = keyword_input.strip()
                
                st.success(f"✅ '{keyword_input}' 관련 키워드 {len(df)}개를 찾았습니다!")
            else:
                st.error("❌ 연관 키워드를 찾을 수 없습니다. 다른 키워드로 시도해보세요.")
    
    elif search_clicked and not keyword_input:
        st.warning("⚠️ 키워드를 입력해주세요.")
    
    # 결과 표시
    if 'keywords_result' in st.session_state and not st.session_state.keywords_result.empty:
        df = st.session_state.keywords_result
        base_keyword = st.session_state.get('base_keyword', '키워드')
        
        st.markdown("---")
        st.markdown(f"## 📊 '{base_keyword}' 연관 키워드 분석 결과")
        
        # 요약 메트릭
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: var(--mint-dark); margin: 0;">🔍 총 키워드 수</h3>
                <p style="font-size: 2rem; font-weight: bold; margin: 0.5rem 0 0 0;">{}</p>
            </div>
            """.format(len(df)), unsafe_allow_html=True)
        
        with col2:
            if 'monthlyPcQcCnt' in df.columns and not df['monthlyPcQcCnt'].empty:
                avg_search = int(df['monthlyPcQcCnt'].mean())
            else:
                avg_search = 0
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: var(--mint-dark); margin: 0;">📈 평균 검색량</h3>
                <p style="font-size: 2rem; font-weight: bold; margin: 0.5rem 0 0 0;">{:,}</p>
            </div>
            """.format(avg_search), unsafe_allow_html=True)
        
        with col3:
            if 'monthlyPcQcCnt' in df.columns and not df['monthlyPcQcCnt'].empty:
                max_search = int(df['monthlyPcQcCnt'].max())
            else:
                max_search = 0
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: var(--mint-dark); margin: 0;">🚀 최고 검색량</h3>
                <p style="font-size: 2rem; font-weight: bold; margin: 0.5rem 0 0 0;">{:,}</p>
            </div>
            """.format(max_search), unsafe_allow_html=True)
        
        with col4:
            if 'compIdx' in df.columns and not df['compIdx'].empty:
                avg_competition = df['compIdx'].mean()
            else:
                avg_competition = 0
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: var(--mint-dark); margin: 0;">⚔️ 평균 경쟁도</h3>
                <p style="font-size: 2rem; font-weight: bold; margin: 0.5rem 0 0 0;">{:.1f}</p>
            </div>
            """.format(avg_competition), unsafe_allow_html=True)
        
        # 키워드 목록
        st.markdown("### 📋 연관 키워드 목록")
        
        for idx, row in df.iterrows():
            # 키워드명 (안전하게 가져오기)
            keyword = row.get('relKeyword', row.get('keyword', f'키워드_{idx}'))
            
            # 검색량 (안전하게 가져오기)
            search_count = 0
            if 'monthlyPcQcCnt' in row and pd.notna(row['monthlyPcQcCnt']):
                search_count = int(row['monthlyPcQcCnt'])
            elif 'searchCount' in row and pd.notna(row['searchCount']):
                search_count = int(row['searchCount'])
            
            # 경쟁도 (안전하게 가져오기)
            competition = 0
            if 'compIdx' in row and pd.notna(row['compIdx']):
                competition = float(row['compIdx'])
            elif 'competition' in row and pd.notna(row['competition']):
                competition = float(row['competition'])
            
            # 경쟁도에 따른 색상 결정
            if competition >= 80:
                comp_color = "🔴"
                comp_text = "높음"
            elif competition >= 50:
                comp_color = "🟡"
                comp_text = "보통"
            else:
                comp_color = "🟢"
                comp_text = "낮음"
            
            st.markdown(f"""
            <div class="keyword-item">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h4 style="margin: 0; color: var(--mint-dark);">🔗 {keyword}</h4>
                    </div>
                    <div style="text-align: right;">
                        <span style="font-size: 1.1rem; font-weight: bold;">📊 {search_count:,}</span><br>
                        <span style="font-size: 0.9rem;">{comp_color} 경쟁도: {comp_text} ({competition:.1f})</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # 차트 시각화
        st.markdown("### 📈 시각화 차트")
        
        # 차트용 데이터 준비
        chart_df = df.copy()
        chart_df = chart_df.head(15)  # 상위 15개만 표시
        
        # 검색량 차트 (데이터가 있을 때만)
        search_col = None
        keyword_col = None
        competition_col = None
        
        # 사용 가능한 컬럼 찾기
        for col in ['monthlyPcQcCnt', 'searchCount', 'search_volume']:
            if col in chart_df.columns:
                search_col = col
                break
        
        for col in ['relKeyword', 'keyword', 'name']:
            if col in chart_df.columns:
                keyword_col = col
                break
                
        for col in ['compIdx', 'competition', 'comp']:
            if col in chart_df.columns:
                competition_col = col
                break
        
        if search_col and keyword_col:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader("🔍 키워드별 검색량")
            
            try:
                chart = alt.Chart(chart_df).mark_bar(color='#40E0D0').encode(
                    x=alt.X(f'{search_col}:Q', title='검색량'),
                    y=alt.Y(f'{keyword_col}:N', sort='-x', title='키워드'),
                    tooltip=[f'{keyword_col}:N', f'{search_col}:Q'] + ([f'{competition_col}:Q'] if competition_col else [])
                ).properties(height=400)
                
                st.altair_chart(chart, use_container_width=True)
            except Exception as e:
                st.warning(f"차트를 생성할 수 없습니다: {str(e)}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # 경쟁도 vs 검색량 산점도 (두 데이터가 모두 있을 때만)
        if search_col and competition_col and keyword_col:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader("⚔️ 경쟁도 vs 검색량 관계")
            
            try:
                scatter_chart = alt.Chart(chart_df).mark_circle(size=100, color='#20B2AA').encode(
                    x=alt.X(f'{competition_col}:Q', title='경쟁도'),
                    y=alt.Y(f'{search_col}:Q', title='검색량'),
                    tooltip=[f'{keyword_col}:N', f'{search_col}:Q', f'{competition_col}:Q']
                ).properties(height=400)
                
                st.altair_chart(scatter_chart, use_container_width=True)
            except Exception as e:
                st.warning(f"산점도를 생성할 수 없습니다: {str(e)}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # 데이터가 없는 경우 안내
        if not search_col:
            st.info("📊 차트를 표시하기 위한 검색량 데이터가 없습니다.")
        
        # 다운로드 섹션
        st.markdown('<div class="download-section">', unsafe_allow_html=True)
        st.markdown("### 💾 데이터 다운로드")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # CSV 다운로드
            csv_data = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📁 CSV 파일 다운로드",
                data=csv_data,
                file_name=f"연관키워드_{base_keyword}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with col2:
            # Excel 다운로드 (간단한 방법)
            st.info("💡 Excel 형태로 다운로드하려면 CSV 파일을 Excel에서 열어보세요!")
        
        st.markdown('</div>', unsafe_allow_html=True)

def main():
    """연관 키워드 페이지 메인"""
    # 페이지 설정
    st.set_page_config(
        page_title="연관 키워드 - " + AppConfig.APP_TITLE,
        page_icon="🔗",
        layout=AppConfig.LAYOUT,
        initial_sidebar_state="expanded"
    )
    
    # 세션 초기화
    initialize_session()
    
    # 인증 확인
    if is_logged_in():
        render_related_keywords_page()
        
        # 푸터
        st.markdown("---")
        st.markdown(
            f"""
            <div style='text-align: center; color: gray; font-size: 12px;'>
            {AppConfig.COPYRIGHT_TEXT}<br>
            네이버 검색광고 API를 활용한 연관 키워드 분석 도구<br>
            Powered by Naver Search AD API v1.0
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.error("로그인이 필요합니다.")
        if st.button("로그인 페이지로 이동"):
            st.switch_page("app.py")

if __name__ == "__main__":
    main()