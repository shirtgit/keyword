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

def safe_float_conversion(value):
    """안전한 float 변환 함수"""
    if pd.isna(value):
        return 0
    
    try:
        return float(value)
    except (ValueError, TypeError):
        # 문자열 경쟁도를 숫자로 변환
        if isinstance(value, str):
            value = value.lower()
            if '높음' in value or 'high' in value:
                return 80
            elif '보통' in value or 'medium' in value or '중간' in value:
                return 50
            elif '낮음' in value or 'low' in value:
                return 20
        return 0

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
    .main .block-container { padding-top: 2rem; padding-left: 4rem; padding-right: 4rem; max-width: 1400px; margin-left: auto; margin-right: auto; }
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
                
                # 정렬 (새로운 데이터 구조에 맞게 처리)
                if sort_by == "검색량":
                    # 새로운 컬럼명으로 정렬
                    if 'total_monthly_search' in df.columns:
                        df = df.sort_values('total_monthly_search', ascending=False)
                    elif 'monthlyPcQcCnt' in df.columns:
                        df = df.sort_values('monthlyPcQcCnt', ascending=False)
                elif sort_by == "경쟁도":
                    if 'competition_index' in df.columns:
                        df = df.sort_values('competition_index', ascending=False)
                    elif 'compIdx' in df.columns:
                        df = df.sort_values('compIdx', ascending=False)
                elif sort_by == "키워드명":
                    # 키워드명으로 정렬
                    if 'keyword' in df.columns:
                        df = df.sort_values('keyword')
                    elif 'relKeyword' in df.columns:
                        df = df.sort_values('relKeyword')
                else:
                    # 기본적으로 검색량으로 정렬
                    if 'total_monthly_search' in df.columns:
                        df = df.sort_values('total_monthly_search', ascending=False)
                    else:
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
            # 새로운 데이터 구조에서 평균 검색량 계산
            if 'total_monthly_search' in df.columns and not df['total_monthly_search'].empty:
                avg_search = int(df['total_monthly_search'].mean())
            elif 'monthlyPcQcCnt' in df.columns and not df['monthlyPcQcCnt'].empty:
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
            # 새로운 데이터 구조에서 최고 검색량 계산
            if 'total_monthly_search' in df.columns and not df['total_monthly_search'].empty:
                max_search = int(df['total_monthly_search'].max())
            elif 'monthlyPcQcCnt' in df.columns and not df['monthlyPcQcCnt'].empty:
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
            # 새로운 데이터 구조에서 평균 클릭률 표시
            if 'total_monthly_avg_ctr' in df.columns and not df['total_monthly_avg_ctr'].empty:
                avg_ctr = df['total_monthly_avg_ctr'].mean()
            else:
                avg_ctr = 0
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: var(--mint-dark); margin: 0;">📊 평균 CTR</h3>
                <p style="font-size: 2rem; font-weight: bold; margin: 0.5rem 0 0 0;">{:.2f}%</p>
            </div>
            """.format(avg_ctr), unsafe_allow_html=True)
        
        # 키워드 목록
        st.markdown("### 📋 연관 키워드 목록")
        
        for idx, row in df.iterrows():
            # 키워드명 (새로운 구조에서 가져오기)
            keyword = row.get('keyword', row.get('relKeyword', f'키워드_{idx}'))
            
            # 통계 데이터 (새로운 구조에서 가져오기)
            total_search = int(row.get('total_monthly_search', 0))
            pc_search = int(row.get('monthly_pc_search', 0))
            mobile_search = int(row.get('monthly_mobile_search', 0))
            
            total_click = int(row.get('total_monthly_avg_click', 0))
            pc_click = int(row.get('monthly_avg_pc_click', 0))
            mobile_click = int(row.get('monthly_avg_mobile_click', 0))
            
            total_ctr = row.get('total_monthly_avg_ctr', 0)
            pc_ctr = row.get('monthly_avg_pc_ctr', 0)
            mobile_ctr = row.get('monthly_avg_mobile_ctr', 0)
            
            competition_level = row.get('competition_level', '알 수 없음')
            competition_index = row.get('competition_index', 'N/A')
            
            # 경쟁도에 따른 색상 결정
            if competition_level == '높음':
                comp_color = "🔴"
            elif competition_level == '보통':
                comp_color = "🟡"
            else:
                comp_color = "🟢"
            
            # 상세 정보가 포함된 카드 표시
            st.markdown(f"""
            <div class="keyword-item" style="background: white; border: 1px solid #e0e0e0; border-radius: 8px; padding: 1rem; margin: 0.5rem 0;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div style="flex: 1;">
                        <h4 style="margin: 0 0 0.5rem 0; color: #20B2AA;">🔗 {keyword}</h4>
                        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; font-size: 0.9rem;">
                            <div>
                                <strong>📱 총 검색량:</strong> {total_search:,}<br>
                                <span style="color: #666;">PC: {pc_search:,} | 모바일: {mobile_search:,}</span>
                            </div>
                            <div>
                                <strong>👆 총 클릭수:</strong> {total_click:,}<br>
                                <span style="color: #666;">PC: {pc_click:,} | 모바일: {mobile_click:,}</span>
                            </div>
                            <div>
                                <strong>📊 평균 CTR:</strong> {total_ctr:.2f}%<br>
                                <span style="color: #666;">PC: {pc_ctr:.2f}% | 모바일: {mobile_ctr:.2f}%</span>
                            </div>
                        </div>
                    </div>
                    <div style="text-align: right; min-width: 120px;">
                        <div style="font-size: 1.2rem; font-weight: bold; margin-bottom: 0.5rem;">
                            � {total_search:,}
                        </div>
                        <div style="font-size: 0.9rem;">
                            {comp_color} 경쟁도: {competition_level}
                        </div>
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
        
        # 새로운 데이터 구조에서 컬럼 찾기
        search_col = None
        keyword_col = None
        click_col = None
        ctr_col = None
        
        # 검색량 컬럼
        for col in ['total_monthly_search', 'monthlyPcQcCnt', 'searchCount']:
            if col in chart_df.columns:
                search_col = col
                break
        
        # 키워드 컬럼
        for col in ['keyword', 'relKeyword', 'name']:
            if col in chart_df.columns:
                keyword_col = col
                break
        
        # 클릭수 컬럼
        for col in ['total_monthly_avg_click', 'monthly_avg_pc_click']:
            if col in chart_df.columns:
                click_col = col
                break
                
        # CTR 컬럼
        for col in ['total_monthly_avg_ctr', 'monthly_avg_pc_ctr']:
            if col in chart_df.columns:
                ctr_col = col
                break
        
        # 1. 검색량 차트
        if search_col and keyword_col:
            st.subheader("🔍 키워드별 검색량")
            try:
                search_chart = alt.Chart(chart_df).mark_bar(color='#40E0D0').encode(
                    x=alt.X(f'{search_col}:Q', title='월간 검색량'),
                    y=alt.Y(f'{keyword_col}:N', sort='-x', title='키워드'),
                    tooltip=[
                        alt.Tooltip(f'{keyword_col}:N', title='키워드'),
                        alt.Tooltip(f'{search_col}:Q', title='월간 검색량', format=',')
                    ] + ([alt.Tooltip(f'{click_col}:Q', title='월간 클릭수', format=',')] if click_col else [])
                ).properties(height=400)
                
                st.altair_chart(search_chart, use_container_width=True)
            except Exception as e:
                st.warning(f"검색량 차트를 생성할 수 없습니다: {str(e)}")
        
        # 2. 클릭수 차트
        if click_col and keyword_col:
            st.subheader("👆 키워드별 클릭수")
            try:
                click_chart = alt.Chart(chart_df).mark_bar(color='#20B2AA').encode(
                    x=alt.X(f'{click_col}:Q', title='월간 클릭수'),
                    y=alt.Y(f'{keyword_col}:N', sort='-x', title='키워드'),
                    tooltip=[
                        alt.Tooltip(f'{keyword_col}:N', title='키워드'),
                        alt.Tooltip(f'{click_col}:Q', title='월간 클릭수', format=','),
                        alt.Tooltip(f'{search_col}:Q', title='월간 검색량', format=',')
                    ]
                ).properties(height=400)
                
                st.altair_chart(click_chart, use_container_width=True)
            except Exception as e:
                st.warning(f"클릭수 차트를 생성할 수 없습니다: {str(e)}")
        
        # 3. CTR 차트
        if ctr_col and keyword_col:
            st.subheader("📊 키워드별 클릭률 (CTR)")
            try:
                ctr_chart = alt.Chart(chart_df).mark_bar(color='#48D1CC').encode(
                    x=alt.X(f'{ctr_col}:Q', title='클릭률 (%)'),
                    y=alt.Y(f'{keyword_col}:N', sort='-x', title='키워드'),
                    tooltip=[
                        alt.Tooltip(f'{keyword_col}:N', title='키워드'),
                        alt.Tooltip(f'{ctr_col}:Q', title='클릭률 (%)', format='.2f')
                    ]
                ).properties(height=400)
                
                st.altair_chart(ctr_chart, use_container_width=True)
            except Exception as e:
                st.warning(f"CTR 차트를 생성할 수 없습니다: {str(e)}")
        
        # 4. 검색량 vs 클릭수 산점도
        if search_col and click_col and keyword_col:
            st.subheader("📈 검색량 vs 클릭수 관계")
            try:
                scatter_chart = alt.Chart(chart_df).mark_circle(size=100, color='#20B2AA').encode(
                    x=alt.X(f'{search_col}:Q', title='월간 검색량'),
                    y=alt.Y(f'{click_col}:Q', title='월간 클릭수'),
                    tooltip=[
                        alt.Tooltip(f'{keyword_col}:N', title='키워드'),
                        alt.Tooltip(f'{search_col}:Q', title='월간 검색량', format=','),
                        alt.Tooltip(f'{click_col}:Q', title='월간 클릭수', format=','),
                        alt.Tooltip(f'{ctr_col}:Q', title='CTR (%)', format='.2f')
                    ]
                ).properties(height=400)
                
                st.altair_chart(scatter_chart, use_container_width=True)
            except Exception as e:
                st.warning(f"산점도를 생성할 수 없습니다: {str(e)}")
        
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