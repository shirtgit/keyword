"""
키워드 상세 분석 페이지
네이버 검색광고 API를 활용한 키워드별 상세 통계 분석
월간검색수, 월평균클릭수, 월평균클릭률, 경쟁정도, 월평균노출, 광고수 등 포함
"""

import streamlit as st
import pandas as pd
import time
from api import get_detailed_keyword_stats
from config import AppConfig
from auth import initialize_session, is_logged_in, logout_user

def render_navigation_sidebar():
    """사이드바 네비게이션 렌더링"""
    with st.sidebar:
        st.markdown("### 🧭 페이지 네비게이션")
        
        # 현재 페이지 표시
        current_page = "📊 키워드 상세 분석"
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
        
        if st.button("📊 키워드 상세 분석", use_container_width=True, disabled=True):
            st.switch_page("pages/4_📊_키워드_상세_분석.py")
        
        if st.button("✍️ 글 재작성", use_container_width=True):
            st.switch_page("pages/5_✍️_글_재작성.py")
        
        if st.button("⚙️ 설정", use_container_width=True):
            st.switch_page("pages/3_⚙️_설정.py")
        
        st.markdown("---")
        
        # 현재 페이지 기능 설명
        st.markdown("### 📊 상세 분석 기능")
        st.markdown("""
        - 🔍 월간검색수 (PC/모바일)
        - 👆 월평균클릭수 분석
        - 📈 월평균클릭률(CTR)
        - ⚔️ 경쟁정도 지수
        - 👁️ 월평균노출수
        - 📢 광고수 추정
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

def render_keyword_detail_analysis_page():
    """키워드 상세 분석 페이지 렌더링"""
    # 다크모드/라이트모드 대응 CSS
    st.markdown("""
    <style>
    /* 컨테이너 최적화 */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 4rem;
        padding-right: 4rem;
        max-width: 1400px;
        margin-left: auto;
        margin-right: auto;
    }
    
    /* 헤더 스타일 */
    .page-header {
        background: linear-gradient(135deg, #20B2AA, #48D1CC);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(32, 178, 170, 0.3);
    }
    
    .page-title {
        color: white !important;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0;
    }
    
    .page-subtitle {
        color: rgba(255,255,255,0.9) !important;
        font-size: 1rem;
        margin: 0.5rem 0 0 0;
    }
    
    /* 버튼 스타일 */
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
    
    /* 결과 카드 스타일 */
    .result-card {
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
    <div class="page-header">
        <h1 class="page-title">📊 키워드 상세 분석</h1>
        <p class="page-subtitle">네이버 검색광고 API로 키워드의 완전한 통계 분석을 수행하세요</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 기능 설명 - 스타일 개선
    st.markdown("""
    <div style='background: linear-gradient(135deg, rgba(32, 178, 170, 0.1), rgba(72, 209, 204, 0.1)); 
                border-left: 4px solid #20B2AA; 
                border-radius: 8px; 
                padding: 1.5rem; 
                margin-bottom: 1.5rem;'>
        <h3 style='color: #20B2AA; margin-top: 0;'>📊 키워드 상세 분석 기능</h3>
        <ul style='margin-bottom: 0; line-height: 1.8;'>
            <li><strong>🔍 월간검색수:</strong> PC/모바일 분리된 정확한 검색량 데이터</li>
            <li><strong>👆 월평균클릭수:</strong> 광고 클릭수 통계 (PC/모바일)</li>
            <li><strong>📈 월평균클릭률(CTR):</strong> 검색 대비 클릭 전환율</li>
            <li><strong>⚔️ 경쟁정도:</strong> 키워드 광고 경쟁 강도 지수</li>
            <li><strong>👁️ 월평균노출수:</strong> 광고 노출 빈도 추정</li>
            <li><strong>📢 광고수 추정:</strong> 경쟁 광고주 수 예측</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # 사이드바에 도움말 표시
    with st.sidebar:
        st.success("### 🎯 전문 마케팅 분석")
        st.markdown("""
        **완전한 키워드 분석:**
        - 📊 검색량 + 클릭 데이터
        - 💡 CTR 및 전환 분석
        - 🎯 경쟁 강도 파악
        - ✨ ROI 예측 지원
        """)
        
        # 분석 지표 설명
        with st.expander("📖 분석 지표 설명"):
            st.markdown("""
            **월간검색수**: 해당 키워드로 월간 검색한 횟수
            
            **월평균클릭수**: 광고를 클릭한 평균 횟수
            
            **월평균클릭률(CTR)**: 
            (클릭수 ÷ 검색수) × 100
            
            **경쟁정도**: 
            - 낮음 (0-30): 경쟁 약함
            - 보통 (31-70): 경쟁 보통
            - 높음 (71-100): 경쟁 치열
            
            **노출수**: 광고가 노출된 예상 횟수
            
            **광고수**: 해당 키워드에 광고하는 예상 광고주 수
            """)
    
    # 메인 입력 영역
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # 키워드 입력
        target_keyword = st.text_input(
            "🎯 분석할 키워드 입력",
            placeholder="예: 키보드",
            key="detail_keyword",
            help="상세 분석하고자 하는 키워드를 입력하세요"
        )
        
        # 분석 옵션
        st.subheader("🔧 분석 옵션")
        
        col_opt1, col_opt2 = st.columns(2)
        with col_opt1:
            show_charts = st.checkbox(
                "📊 차트 시각화",
                value=True,
                help="분석 결과를 차트로 시각화"
            )
            
            show_comparison = st.checkbox(
                "📈 PC vs 모바일 비교",
                value=True,
                help="PC와 모바일 데이터 비교 분석"
            )
        
        with col_opt2:
            detail_level = st.selectbox(
                "📋 분석 상세도",
                options=["기본", "상세", "전문가"],
                index=1,
                help="분석 결과의 상세 정도 선택"
            )
            
            sort_by = st.selectbox(
                "📈 정렬 기준",
                options=["검색량", "클릭률", "경쟁도", "키워드명"],
                index=0,
                help="결과를 어떤 기준으로 정렬할지 선택"
            )
        
        # 검색 버튼
        analyze_button = st.button(
            "📊 키워드 상세 분석 시작", 
            type="primary", 
            use_container_width=True, 
            key="detail_analyze"
        )
    
    with col2:
        st.markdown("### 💡 간단 가이드")
        st.info("""
        **1단계**: 분석할 키워드 입력
        **2단계**: 분석 옵션 설정
        **3단계**: 상세도 및 정렬 선택
        **4단계**: 상세 분석 시작 버튼 클릭
        """)
    
    # 키워드 상세 분석 가이드를 버튼 아래로 이동
    st.markdown("---")
    st.markdown("### 📖 키워드 상세 분석 가이드")
    
    # 3개 칼럼으로 가이드 배치 - 스타일 개선
    guide_col1, guide_col2, guide_col3 = st.columns(3)
    
    with guide_col1:
        st.markdown("""
        <div style='background: linear-gradient(135deg, rgba(32, 178, 170, 0.08), rgba(72, 209, 204, 0.08)); 
                    border: 1px solid rgba(32, 178, 170, 0.3); 
                    border-radius: 8px; 
                    padding: 1.2rem; 
                    height: 100%;'>
            <h3 style='color: #20B2AA; font-size: 1.1rem; margin-top: 0;'>🎯 마케팅 전략 수립</h3>
            <ul style='margin-bottom: 0; line-height: 1.6; font-size: 0.9rem;'>
                <li><strong>기회 키워드:</strong> 높은 CTR + 낮은 경쟁도</li>
                <li><strong>주력 키워드:</strong> 높은 검색량 + 높은 경쟁도</li>
                <li><strong>최적화 필요:</strong> 낮은 CTR 키워드 개선</li>
                <li><strong>롱테일 발굴:</strong> 구체적이고 긴 키워드 조합</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with guide_col2:
        st.markdown("""
        <div style='background: linear-gradient(135deg, rgba(32, 178, 170, 0.08), rgba(72, 209, 204, 0.08)); 
                    border: 1px solid rgba(72, 209, 204, 0.3); 
                    border-radius: 8px; 
                    padding: 1.2rem; 
                    height: 100%;'>
            <h3 style='color: #48D1CC; font-size: 1.1rem; margin-top: 0;'>📊 ROI 분석 포인트</h3>
            <ul style='margin-bottom: 0; line-height: 1.6; font-size: 0.9rem;'>
                <li><strong>클릭률 우선:</strong> CTR이 높은 키워드 집중</li>
                <li><strong>경쟁도 고려:</strong> 경쟁도 대비 검색량 분석</li>
                <li><strong>디바이스 분석:</strong> PC vs 모바일 비중 파악</li>
                <li><strong>효율성 계산:</strong> 광고비 대비 전환율 예측</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with guide_col3:
        st.markdown("""
        <div style='background: linear-gradient(135deg, rgba(32, 178, 170, 0.08), rgba(72, 209, 204, 0.08)); 
                    border: 1px solid rgba(255, 193, 7, 0.3); 
                    border-radius: 8px; 
                    padding: 1.2rem; 
                    height: 100%;'>
            <h3 style='color: #FFA500; font-size: 1.1rem; margin-top: 0;'>⚠️ 주의사항 및 한계</h3>
            <ul style='margin-bottom: 0; line-height: 1.6; font-size: 0.9rem;'>
                <li><strong>계절성 키워드:</strong> 시기별 검색량 변동 고려</li>
                <li><strong>브랜드 키워드:</strong> 타사 브랜드명 사용 주의</li>
                <li><strong>예산 효율성:</strong> 광고비 예산 대비 ROI 계산</li>
                <li><strong>데이터 변동:</strong> 실시간 데이터로 수시 변경</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # 분석 실행
    if analyze_button:
        if not target_keyword.strip():
            st.error("❌ 분석할 키워드를 입력해주세요.")
            return
        
        st.success(f"🔄 '{target_keyword}' 키워드의 상세 분석을 시작합니다...")
        
        # 프로그레스 바와 상태 텍스트
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("🎯 네이버 검색광고 API에서 상세 데이터를 수집하는 중...")
        progress_bar.progress(0.3)
        
        # 상세 키워드 분석
        detailed_stats = get_detailed_keyword_stats(target_keyword)
        
        progress_bar.progress(0.7)
        status_text.text("📊 데이터 처리 및 분석 중...")
        
        time.sleep(0.5)  # 처리 시간 시뮬레이션
        
        progress_bar.progress(1.0)
        status_text.text("✅ 키워드 상세 분석이 완료되었습니다!")
        
        if detailed_stats:
            st.markdown("---")
            st.subheader(f"📊 '{target_keyword}'의 상세 분석 결과")
            
            # 결과를 DataFrame으로 변환
            df = pd.DataFrame(detailed_stats)
            
            # 정렬 적용
            if sort_by == "검색량":
                df = df.sort_values('total_monthly_search', ascending=False)
            elif sort_by == "클릭률":
                df = df.sort_values('total_monthly_avg_ctr', ascending=False)
            elif sort_by == "경쟁도":
                df = df.sort_values('competition_index', ascending=False)
            elif sort_by == "키워드명":
                df = df.sort_values('keyword')
            
            # 전체 통계 요약
            st.subheader("📈 전체 분석 요약")
            col_summary1, col_summary2, col_summary3, col_summary4 = st.columns(4)
            
            with col_summary1:
                total_keywords = len(df)
                st.metric("🔗 분석 키워드 수", total_keywords)
            
            with col_summary2:
                avg_search = df['total_monthly_search'].mean()
                st.metric("📊 평균 월간검색수", f"{int(avg_search):,}")
            
            with col_summary3:
                avg_ctr = df['total_monthly_avg_ctr'].mean()
                st.metric("📈 평균 클릭률", f"{avg_ctr:.2f}%")
            
            with col_summary4:
                high_competition = len(df[df['competition_level'] == '높음'])
                st.metric("⚔️ 고경쟁 키워드", f"{high_competition}개")
            
            # 차트 시각화 (옵션에 따라)
            if show_charts:
                st.subheader("📊 데이터 시각화")
                
                # 탭으로 차트 구분
                chart_tab1, chart_tab2, chart_tab3 = st.tabs(["🔍 검색량 분석", "📈 클릭률 분석", "⚔️ 경쟁도 분석"])
                
                with chart_tab1:
                    # 검색량 차트
                    st.markdown("#### 월간 검색량 상위 키워드")
                    
                    top_search_keywords = df.head(15)
                    
                    if show_comparison:
                        # PC vs 모바일 비교 차트
                        import altair as alt
                        
                        # 데이터 준비
                        chart_data = []
                        for _, row in top_search_keywords.iterrows():
                            chart_data.append({
                                'keyword': row['keyword'],
                                'PC 검색량': row['monthly_pc_search'],
                                'type': 'PC'
                            })
                            chart_data.append({
                                'keyword': row['keyword'],
                                'PC 검색량': row['monthly_mobile_search'],
                                'type': '모바일'
                            })
                        
                        chart_df = pd.DataFrame(chart_data)
                        
                        chart = alt.Chart(chart_df).mark_bar().encode(
                            x=alt.X('PC 검색량:Q', title='월간 검색량'),
                            y=alt.Y('keyword:N', sort='-x', title='키워드'),
                            color=alt.Color('type:N', title='디바이스'),
                            tooltip=['keyword', 'PC 검색량', 'type']
                        ).properties(
                            height=400,
                            title="PC vs 모바일 월간 검색량 비교"
                        ).resolve_scale(
                            color='independent'
                        )
                        
                        st.altair_chart(chart, use_container_width=True)
                    else:
                        # 단순 총 검색량 차트
                        import altair as alt
                        
                        chart = alt.Chart(top_search_keywords).mark_bar(
                            color='steelblue',
                            opacity=0.8
                        ).encode(
                            x=alt.X('total_monthly_search:Q', title='월간 총 검색량'),
                            y=alt.Y('keyword:N', sort='-x', title='키워드'),
                            tooltip=[
                                alt.Tooltip('keyword:N', title='키워드'),
                                alt.Tooltip('total_monthly_search:Q', title='총 검색량', format=',.0f'),
                                alt.Tooltip('monthly_pc_search:Q', title='PC 검색량', format=',.0f'),
                                alt.Tooltip('monthly_mobile_search:Q', title='모바일 검색량', format=',.0f')
                            ]
                        ).properties(
                            height=400,
                            title="월간 검색량 상위 키워드"
                        )
                        
                        st.altair_chart(chart, use_container_width=True)
                
                with chart_tab2:
                    # 클릭률 차트
                    st.markdown("#### 클릭률(CTR) 상위 키워드")
                    
                    # 클릭률이 0보다 큰 키워드만 필터링
                    ctr_keywords = df[df['total_monthly_avg_ctr'] > 0].head(15)
                    
                    if len(ctr_keywords) > 0:
                        import altair as alt
                        
                        chart = alt.Chart(ctr_keywords).mark_bar(
                            color='orange',
                            opacity=0.8
                        ).encode(
                            x=alt.X('total_monthly_avg_ctr:Q', title='평균 클릭률 (%)'),
                            y=alt.Y('keyword:N', sort='-x', title='키워드'),
                            tooltip=[
                                alt.Tooltip('keyword:N', title='키워드'),
                                alt.Tooltip('total_monthly_avg_ctr:Q', title='평균 클릭률', format='.2f'),
                                alt.Tooltip('total_monthly_avg_click:Q', title='평균 클릭수', format=',.0f'),
                                alt.Tooltip('total_monthly_search:Q', title='검색량', format=',.0f')
                            ]
                        ).properties(
                            height=400,
                            title="클릭률(CTR) 상위 키워드"
                        )
                        
                        st.altair_chart(chart, use_container_width=True)
                    else:
                        st.warning("클릭률 데이터가 있는 키워드가 없습니다.")
                
                with chart_tab3:
                    # 경쟁도 vs 검색량 산점도
                    st.markdown("#### 경쟁도 vs 검색량 분석")
                    
                    # 경쟁도가 있는 키워드만 필터링 - 안전한 처리
                    comp_keywords = df[(df['competition_index'] != 'N/A') & (df['competition_index'].notna())].head(20)
                    
                    if len(comp_keywords) > 0:
                        import altair as alt
                        
                        # 경쟁도를 숫자로 변환 - 안전한 처리
                        comp_keywords = comp_keywords.copy()
                        
                        def safe_convert_competition(value):
                            """경쟁도 값을 안전하게 숫자로 변환"""
                            if pd.isna(value) or value == 'N/A':
                                return 50  # 기본값
                            if isinstance(value, str):
                                if value == '낮음':
                                    return 20
                                elif value == '보통':
                                    return 50
                                elif value == '높음':
                                    return 80
                                else:
                                    try:
                                        return float(value)
                                    except:
                                        return 50
                            try:
                                return float(value)
                            except:
                                return 50
                        
                        comp_keywords['competition_numeric'] = comp_keywords['competition_index'].apply(safe_convert_competition)
                        
                        scatter = alt.Chart(comp_keywords).mark_circle(
                            size=100,
                            opacity=0.7
                        ).encode(
                            x=alt.X('competition_numeric:Q', title='경쟁도 지수'),
                            y=alt.Y('total_monthly_search:Q', title='월간 검색량'),
                            color=alt.Color('competition_level:N', title='경쟁 수준'),
                            tooltip=[
                                alt.Tooltip('keyword:N', title='키워드'),
                                alt.Tooltip('competition_numeric:Q', title='경쟁도 지수', format='.1f'),
                                alt.Tooltip('total_monthly_search:Q', title='검색량', format=',.0f'),
                                alt.Tooltip('competition_level:N', title='경쟁 수준')
                            ]
                        ).properties(
                            height=400,
                            title="경쟁도 vs 검색량 분포"
                        )
                        
                        st.altair_chart(scatter, use_container_width=True)
                    else:
                        st.warning("경쟁도 데이터가 있는 키워드가 없습니다.")
            
            # 상세 데이터 테이블
            st.subheader("📋 상세 분석 데이터")
            
            # 필터링 옵션
            col_filter1, col_filter2, col_filter3 = st.columns(3)
            
            with col_filter1:
                keyword_filter = st.text_input(
                    "🔍 키워드 검색",
                    placeholder="특정 키워드 검색...",
                    key="detail_keyword_filter"
                )
            
            with col_filter2:
                min_search_filter = st.number_input(
                    "📊 최소 검색량",
                    min_value=0,
                    value=0,
                    step=100,
                    help="입력한 검색량 이상의 키워드만 표시"
                )
            
            with col_filter3:
                competition_filter = st.selectbox(
                    "⚔️ 경쟁도 필터",
                    options=["전체", "낮음", "보통", "높음", "알 수 없음"],
                    key="detail_competition_filter"
                )
            
            # 필터링 적용
            filtered_df = df.copy()
            
            if keyword_filter:
                filtered_df = filtered_df[filtered_df['keyword'].str.contains(keyword_filter, case=False, na=False)]
            
            if min_search_filter > 0:
                filtered_df = filtered_df[filtered_df['total_monthly_search'] >= min_search_filter]
            
            if competition_filter != "전체":
                filtered_df = filtered_df[filtered_df['competition_level'] == competition_filter]
            
            # 결과 개수 정보
            if len(filtered_df) != len(df):
                st.info(f"필터 적용 결과: {len(filtered_df)}개 / 전체 {len(df)}개")
            
            # 테이블 표시 (상세도에 따라 컬럼 선택)
            if detail_level == "기본":
                display_columns = ['keyword', 'total_monthly_search', 'total_monthly_avg_ctr', 'competition_level']
                column_names = ['키워드', '월간 총검색수', '평균 클릭률(%)', '경쟁도']
            elif detail_level == "상세":
                display_columns = ['keyword', 'monthly_pc_search', 'monthly_mobile_search', 
                                 'total_monthly_avg_click', 'total_monthly_avg_ctr', 'competition_level']
                column_names = ['키워드', 'PC 검색수', '모바일 검색수', '평균 클릭수', '평균 클릭률(%)', '경쟁도']
            else:  # 전문가
                display_columns = ['keyword', 'monthly_pc_search', 'monthly_mobile_search',
                                 'monthly_avg_pc_click', 'monthly_avg_mobile_click',
                                 'monthly_avg_pc_ctr', 'monthly_avg_mobile_ctr',
                                 'competition_index', 'estimated_ads_count']
                column_names = ['키워드', 'PC검색수', '모바일검색수', 'PC클릭수', '모바일클릭수',
                              'PC클릭률(%)', '모바일클릭률(%)', '경쟁지수', '예상광고수']
            
            # 표시할 데이터 준비
            display_df = filtered_df[display_columns].copy()
            display_df.columns = column_names
            display_df.index = range(1, len(display_df) + 1)
            
            st.dataframe(
                display_df,
                use_container_width=True,
                height=500,
                column_config={
                    col: st.column_config.NumberColumn(
                        col,
                        format="%.2f" if "클릭률" in col else "%d"
                    ) for col in column_names if col != "키워드" and col != "경쟁도"
                }
            )
            
            # 분석 인사이트
            st.subheader("💡 키워드 분석 인사이트")
            
            # 주요 키워드 추천
            col_insight1, col_insight2 = st.columns(2)
            
            with col_insight1:
                st.markdown("#### 🎯 추천 타겟 키워드")
                
                # 높은 검색량 + 적당한 경쟁도 키워드
                good_keywords = filtered_df[
                    (filtered_df['total_monthly_search'] > filtered_df['total_monthly_search'].median()) &
                    (filtered_df['competition_level'].isin(['낮음', '보통']))
                ].head(5)
                
                if len(good_keywords) > 0:
                    for _, row in good_keywords.iterrows():
                        st.success(f"**{row['keyword']}** - 검색량: {int(row['total_monthly_search']):,}, 경쟁도: {row['competition_level']}")
                else:
                    st.info("현재 필터 조건에서는 추천 키워드가 없습니다.")
            
            with col_insight2:
                st.markdown("#### ⚠️ 주의 키워드")
                
                # 높은 경쟁도 + 낮은 클릭률 키워드
                risky_keywords = filtered_df[
                    (filtered_df['competition_level'] == '높음') &
                    (filtered_df['total_monthly_avg_ctr'] < filtered_df['total_monthly_avg_ctr'].median())
                ].head(5)
                
                if len(risky_keywords) > 0:
                    for _, row in risky_keywords.iterrows():
                        st.warning(f"**{row['keyword']}** - 고경쟁도, 낮은 클릭률 ({row['total_monthly_avg_ctr']:.2f}%)")
                else:
                    st.info("주의가 필요한 키워드가 없습니다.")
            
            # 전략 제안
            st.subheader("🚀 마케팅 전략 제안")
            
            avg_competition = len(df[df['competition_level'] == '높음']) / len(df) * 100
            avg_ctr = df['total_monthly_avg_ctr'].mean()
            
            col_strategy1, col_strategy2, col_strategy3 = st.columns(3)
            
            with col_strategy1:
                if avg_competition > 60:
                    st.error("**고경쟁 시장**\n롱테일 키워드나 니치 키워드 발굴 권장")
                elif avg_competition > 30:
                    st.warning("**보통 경쟁 시장**\n차별화된 광고 크리에이티브 필요")
                else:
                    st.success("**저경쟁 시장**\n적극적인 키워드 확장 기회")
            
            with col_strategy2:
                if avg_ctr > 2.0:
                    st.success("**높은 클릭률**\n현재 키워드 세트 유지 권장")
                elif avg_ctr > 1.0:
                    st.info("**보통 클릭률**\n키워드 최적화로 개선 가능")
                else:
                    st.warning("**낮은 클릭률**\n키워드 재검토 및 광고 개선 필요")
            
            with col_strategy3:
                mobile_ratio = df['monthly_mobile_search'].sum() / df['total_monthly_search'].sum() * 100
                if mobile_ratio > 70:
                    st.info("**모바일 우세**\n모바일 최적화 광고 집중")
                elif mobile_ratio > 40:
                    st.success("**균형적 분포**\nPC/모바일 균형 전략")
                else:
                    st.warning("**PC 우세**\nPC 타겟팅 강화 권장")
            
            # CSV 다운로드
            st.subheader("📥 데이터 저장")
            col_download1, col_download2 = st.columns(2)
            
            with col_download1:
                # 현재 필터된 결과 다운로드
                csv_data = display_df.to_csv(index=True, encoding='utf-8-sig')
                
                st.download_button(
                    label=f"📥 필터된 결과 다운로드 ({len(display_df)}개)",
                    data=csv_data,
                    file_name=f"{target_keyword}_상세분석_필터_{time.strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col_download2:
                # 전체 상세 데이터 다운로드
                full_df = df.copy()
                full_df.index = range(1, len(full_df) + 1)
                full_csv_data = full_df.to_csv(index=True, encoding='utf-8-sig')
                
                st.download_button(
                    label=f"📥 전체 상세 분석 다운로드 ({len(df)}개)",
                    data=full_csv_data,
                    file_name=f"{target_keyword}_상세분석_전체_{time.strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
        else:
            st.warning("❌ 상세 분석 데이터를 찾을 수 없습니다. 다른 키워드로 시도해보세요.")
            
            st.subheader("🔍 분석 개선 제안")
            st.info("""
            **분석 결과가 없는 경우:**
            1. **키워드 변경**: 더 일반적이거나 구체적인 키워드 시도
            2. **API 상태 확인**: 네이버 검색광고 API 연결 상태 확인
            3. **권한 확인**: API 사용 권한 및 한도 확인
            4. **키워드 형태**: 한글 키워드 또는 영문 키워드 시도
            """)

def main():
    """키워드 상세 분석 페이지 메인"""
    # 페이지 설정
    st.set_page_config(
        page_title="키워드 상세 분석 - " + AppConfig.APP_TITLE,
        page_icon="📊",
        layout=AppConfig.LAYOUT,
        initial_sidebar_state="expanded"
    )
    
    # 세션 초기화
    initialize_session()
    
    # 인증 확인
    if is_logged_in():
        render_keyword_detail_analysis_page()
        
        # 푸터
        st.markdown("---")
        st.markdown(
            f"""
            <div style='text-align: center; color: gray; font-size: 12px;'>
            {AppConfig.COPYRIGHT_TEXT}<br>
            키워드 상세 분석 페이지 - 네이버 검색광고 API 전문 분석
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.error("❌ 로그인이 필요합니다.")
        if st.button("🔑 로그인 페이지로 이동", use_container_width=True):
            st.switch_page("app.py")

if __name__ == "__main__":
    main()