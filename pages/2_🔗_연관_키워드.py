"""
연관 키워드 페이지
네이버 검색광고 API를 활용한 키워드 분석 및 연관 키워드 발굴
"""

import streamlit as st
import pandas as pd
import altair as alt
import time
from api import get_related_keywords
from config import AppConfig
from auth import initialize_session, is_logged_in, render_logout_section

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
        
        # 사용자 정보
        current_user = st.session_state.get('username', 'Unknown')
        st.markdown(f"### 👤 사용자: **{current_user}**")

def render_related_keywords_page():
    """연관 키워드 페이지 렌더링"""
    # 민트 테마 CSS 적용
    st.markdown("""
    <style>
    .main .block-container { padding-top: 2rem; max-width: 1200px; }
    :root {
        --mint-primary: #40E0D0; --mint-secondary: #48D1CC; --mint-light: #AFEEEE;
        --mint-dark: #20B2AA; --mint-bg: #F0FFFF; --text-dark: #2C3E50; --text-light: #5D6D7E;
    }
    .page-header {
        background: linear-gradient(135deg, var(--mint-primary), var(--mint-secondary));
        padding: 2rem; border-radius: 15px; margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(64, 224, 208, 0.2);
    }
    .page-title { color: white; font-size: 2.2rem; font-weight: 700; margin: 0; }
    .page-subtitle { color: rgba(255,255,255,0.9); font-size: 1.1rem; margin: 0.5rem 0 0 0; }
    .stButton > button {
        background: linear-gradient(135deg, var(--mint-primary), var(--mint-secondary));
        color: white; border: none; border-radius: 8px; font-weight: 600;
        box-shadow: 0 2px 8px rgba(64, 224, 208, 0.3);
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, var(--mint-secondary), var(--mint-dark));
        transform: translateY(-1px); box-shadow: 0 4px 12px rgba(64, 224, 208, 0.4);
    }
    .css-1d391kg { background-color: var(--mint-bg); }
    </style>
    """, unsafe_allow_html=True)
    
    # 사이드바 네비게이션
    render_navigation_sidebar()
    
    # 헤더
    st.markdown("""
    <div class="page-header">
        <h1 class="page-title">🔗 연관 키워드 분석</h1>
        <p class="page-subtitle">키워드 분석으로 마케팅 전략을 최적화하세요</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 로그아웃 섹션을 우상단에 배치
    col_spacer, col_logout = st.columns([4, 1])
    with col_logout:
        render_logout_section()

import streamlit as st
import pandas as pd
import time
from api import get_related_keywords
from config import AppConfig
from auth import initialize_session, is_logged_in, render_logout_section

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
        
        if st.button("⚙️ 설정", use_container_width=True):
            st.switch_page("pages/3_⚙️_설정.py")
        
        st.markdown("---")
        
        # 현재 페이지 기능 설명
        st.markdown("### 🔗 연관 키워드 기능")
        st.markdown("""
        - 네이버 검색광고 API 전용
        - 공식 마케팅 데이터
        - 검색량 및 경쟁도 분석
        - 차트 및 CSV 다운로드
        """)
        
        # 사용자 정보
        current_user = st.session_state.get('username', 'Unknown')
        st.markdown(f"### 👤 사용자: **{current_user}**")

def render_related_keywords_page():
    """연관 키워드 페이지 렌더링"""
    # 사이드바 네비게이션
    render_navigation_sidebar()
    
    # 헤더
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🔗 연관 키워드 분석")
        st.markdown("**네이버 검색광고 API로 전문적인 키워드 분석을 수행하세요**")
    with col2:
        render_logout_section()
    
    st.markdown("---")
    
    # 기능 설명
    st.info("""
    ### 🎯 연관 키워드 분석 기능
    - **네이버 검색광고 API** 전용 - 공식 마케팅 데이터
    - **검색량과 경쟁도** 정보가 포함된 정확한 분석
    - **PC/모바일** 검색량 분리 제공
    - **차트 시각화**와 **CSV 다운로드** 지원
    - 마케팅 **키워드 최적화**에 최적화
    """)
    
    # 사이드바에 도움말 표시
    with st.sidebar:
        st.success("### 🎯 네이버 검색광고 API")
        st.markdown("""
        **전문 마케팅 데이터 제공:**
        - 📊 공식 검색량 데이터
        - 💡 정확한 경쟁도 분석
        - 🎯 PC/모바일 분리 통계
        - ✨ 마케팅 최적화 지원
        """)
        
        st.info("### 📖 사용 가이드")
        st.markdown("""
        **1. 기준 키워드 입력**
        - 분석하고 싶은 주제 키워드
        
        **2. 옵션 선택**
        - 차트 표시 여부
        - 정렬 기준 선택
        
        **3. 결과 활용**
        - 검색량과 경쟁도 확인
        - CSV로 데이터 저장
        - 마케팅 전략 수립
        """)
        
        st.warning("⚠️ 정확한 마케팅 데이터를 제공합니다.")
        
        # 성공 사례
        with st.expander("🏆 활용 성공 사례"):
            st.markdown("""
            **키워드 최적화:**
            - 롱테일 키워드 발굴
            - 경쟁도 낮은 키워드 선택
            
            **마케팅 전략:**
            - 검색광고 키워드 선정
            - SEO 키워드 계획
            
            **상품 기획:**
            - 트렌드 키워드 파악
            - 고객 니즈 분석
            """)
    
    # 메인 입력 영역
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # 키워드 입력
        base_keyword = st.text_input(
            "🎯 기준 키워드 입력",
            placeholder="예: 키보드",
            key="related_keyword",
            help="분석하고자 하는 기준 키워드를 입력하세요"
        )
        
        # 검색 옵션
        st.subheader("🔧 분석 옵션")
        
        col_opt1, col_opt2 = st.columns(2)
        with col_opt1:
            show_top_chart = st.checkbox(
                "📊 상위 키워드 차트 표시",
                value=True,
                help="상위 20개 키워드를 차트로 시각화"
            )
            
            show_competition = st.checkbox(
                "⚔️ 경쟁도 분석 포함",
                value=True,
                help="키워드별 경쟁도 정보 표시"
            )
        
        with col_opt2:
            sort_option = st.selectbox(
                "📈 결과 정렬 기준",
                options=["검색량순", "키워드명순", "경쟁도순"],
                index=0,
                help="결과를 어떤 기준으로 정렬할지 선택"
            )
            
            result_limit = st.selectbox(
                "📋 표시할 결과 개수",
                options=[20, 50, 100, "전체"],
                index=1,
                help="테이블에 표시할 결과의 개수"
            )
        
        # 검색 버튼
        search_related_button = st.button(
            "🎯 연관 키워드 분석 시작 (검색광고 API)", 
            type="primary", 
            use_container_width=True, 
            key="related_search"
        )
    
    with col2:
        st.markdown("### 💡 간단 가이드")
        st.info("""
        **1단계**: 기준 키워드 입력
        **2단계**: 분석 옵션 선택
        **3단계**: 분석 시작 버튼 클릭
        **4단계**: 결과 확인 및 다운로드
        """)
    
    # 키워드 분석 가이드를 버튼 아래로 이동
    st.markdown("---")
    st.markdown("### 📖 키워드 분석 가이드")
    
    # 3개 칼럼으로 가이드 배치
    guide_col1, guide_col2, guide_col3 = st.columns(3)
    
    with guide_col1:
        st.success("""
        ### 🎯 좋은 키워드의 특징
        - **적절한 검색량**: 너무 높지도 낮지도 않은 검색량
        - **낮은 경쟁도**: 광고 경쟁이 치열하지 않음
        - **높은 관련성**: 사업 분야와 밀접한 연관
        - **구체적 의도**: 명확한 검색 의도를 가진 키워드
        """)
    
    with guide_col2:
        st.info("""
        ### 🚀 검색광고 API 장점
        - **🎯 공식 데이터**: 네이버 검색광고 공식 데이터
        - **📊 정확한 통계**: 실제 검색량과 클릭률 제공
        - **💡 경쟁도 분석**: 실시간 광고 경쟁 상황
        - **✨ 마케팅 최적화**: 전문적인 키워드 전략 수립
        """)
    
    with guide_col3:
        st.warning("""
        ### ⚠️ 주의사항 및 팁
        - **일반적 키워드 지양**: 너무 광범위한 키워드 피하기
        - **브랜드명 주의**: 타사 브랜드명 사용 시 주의
        - **계절성 고려**: 시기별 검색량 변동 고려
        - **롱테일 활용**: 구체적이고 긴 키워드 조합 활용
        """)
    
    # 검색 실행
    if search_related_button:
        if not base_keyword.strip():
            st.error("❌ 기준 키워드를 입력해주세요.")
            return
        
        st.success(f"🔄 '{base_keyword}' 키워드의 연관 키워드를 분석합니다...")
        
        # 프로그레스 바와 상태 텍스트
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("🎯 네이버 검색광고 API에서 전문 마케팅 데이터를 수집하는 중...")
        progress_bar.progress(0.3)
        
        # 연관 키워드 검색
        related_keywords = get_related_keywords(base_keyword)
        
        progress_bar.progress(0.7)
        status_text.text("📊 데이터 처리 및 분석 중...")
        
        time.sleep(0.5)  # 처리 시간 시뮬레이션
        
        progress_bar.progress(1.0)
        status_text.text("✅ 연관 키워드 분석이 완료되었습니다!")
        
        if related_keywords:
            st.markdown("---")
            st.subheader(f"🔗 '{base_keyword}'의 연관 키워드 분석 결과")
            
            # 결과를 DataFrame으로 변환
            df_data = []
            for kw in related_keywords:
                df_data.append({
                    'keyword': kw['keyword'],
                    'pc_search': kw.get('monthly_pc_qc', 0),
                    'mobile_search': kw.get('monthly_mobile_qc', 0),
                    'total_search': kw.get('monthly_pc_qc', 0) + kw.get('monthly_mobile_qc', 0),
                    'competition': kw.get('competition', 'N/A'),
                    'source': '검색광고 API'
                })
            
            df = pd.DataFrame(df_data)
            
            # 정렬 적용
            if sort_option == "검색량순":
                df = df.sort_values('total_search', ascending=False)
            elif sort_option == "키워드명순":
                df = df.sort_values('keyword')
            elif sort_option == "경쟁도순":
                df = df.sort_values('competition')
            
            # 메트릭 표시
            col_metric1, col_metric2, col_metric3, col_metric4 = st.columns(4)
            with col_metric1:
                st.metric("🔗 총 연관 키워드", len(related_keywords))
            with col_metric2:
                st.metric("📡 데이터 소스", "검색광고 API")
            with col_metric3:
                avg_search = df['total_search'].mean()
                st.metric("📊 평균 검색량", f"{int(avg_search):,}")
            with col_metric4:
                total_search = df['total_search'].sum()
                st.metric("📈 총 검색량", f"{int(total_search):,}")
            
            # 상위 키워드를 차트로 표시 (옵션에 따라)
            if show_top_chart:
                st.subheader("📊 상위 연관 키워드 시각화")
                chart_count = min(AppConfig.MAX_CHART_ITEMS, len(df))
                top_keywords = df.head(chart_count)
                
                # 개선된 바 차트
                import altair as alt
                
                # 최대값 계산 (여유 공간 10% 추가)
                max_value = top_keywords['total_search'].max()
                y_max = int(max_value * 1.1) if max_value > 0 else 100
                
                # Altair 차트 생성
                chart = alt.Chart(top_keywords).mark_bar(
                    color='steelblue',
                    opacity=0.8
                ).encode(
                    x=alt.X(
                        'total_search:Q', 
                        title='총 검색량',
                        scale=alt.Scale(domain=[0, y_max]),
                        axis=alt.Axis(format=',.0f')
                    ),
                    y=alt.Y(
                        'keyword:N', 
                        sort='-x', 
                        title='키워드',
                        axis=alt.Axis(labelLimit=150)
                    ),
                    tooltip=[
                        alt.Tooltip('keyword:N', title='키워드'),
                        alt.Tooltip('total_search:Q', title='총 검색량', format=',.0f'),
                        alt.Tooltip('pc_search:Q', title='PC 검색량', format=',.0f'),
                        alt.Tooltip('mobile_search:Q', title='모바일 검색량', format=',.0f'),
                        alt.Tooltip('competition:N', title='경쟁도')
                    ]
                ).properties(
                    height=500,
                    title=alt.TitleParams(
                        text=f"'{base_keyword}' 연관 키워드 검색량 분석 (검색광고 API)",
                        fontSize=16,
                        anchor='start'
                    )
                ).configure_axis(
                    labelFontSize=11,
                    titleFontSize=12
                ).configure_title(
                    fontSize=16,
                    color='#2c3e50'
                )
                
                # 마우스 휠 비활성화 CSS
                st.markdown(
                    """
                    <style>
                    div[data-testid="stVegaLiteChart"] > div {
                        pointer-events: none !important;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True
                )
                
                # 차트 표시
                st.altair_chart(chart, use_container_width=True)
                
                # 경쟁도 분석 차트 (옵션에 따라)
                if show_competition and 'competition' in df.columns:
                    st.subheader("⚔️ 경쟁도 vs 검색량 분산도")
                    
                    # 경쟁도 매핑
                    competition_map = {'낮음': 1, '보통': 2, '높음': 3}
                    top_keywords_comp = top_keywords.copy()
                    top_keywords_comp['competition_num'] = top_keywords_comp['competition'].map(
                        lambda x: competition_map.get(x, 2)
                    )
                    
                    scatter_chart = alt.Chart(top_keywords_comp).mark_circle(
                        size=100,
                        opacity=0.7
                    ).encode(
                        x=alt.X('competition_num:O', title='경쟁도', axis=alt.Axis(labelExpr="datum.value == 1 ? '낮음' : datum.value == 2 ? '보통' : '높음'")),
                        y=alt.Y('total_search:Q', title='총 검색량'),
                        color=alt.Color('competition:N', title='경쟁도'),
                        tooltip=[
                            alt.Tooltip('keyword:N', title='키워드'),
                            alt.Tooltip('total_search:Q', title='검색량', format=',.0f'),
                            alt.Tooltip('competition:N', title='경쟁도')
                        ]
                    ).properties(
                        height=400,
                        title="키워드별 검색량 vs 경쟁도 분석"
                    )
                    
                    st.altair_chart(scatter_chart, use_container_width=True)
            
            # 필터링 옵션
            st.subheader("🔍 결과 필터링")
            col_filter1, col_filter2, col_filter3 = st.columns(3)
            
            with col_filter1:
                search_filter = st.text_input(
                    "🔍 키워드 검색",
                    placeholder="특정 키워드 검색...",
                    key="keyword_filter"
                )
            
            with col_filter2:
                min_search_volume = st.number_input(
                    "📊 최소 검색량",
                    min_value=0,
                    value=0,
                    step=100,
                    help="입력한 검색량 이상의 키워드만 표시"
                )
            
            with col_filter3:
                competition_filter = st.selectbox(
                    "⚔️ 경쟁도 필터",
                    options=["전체", "낮음", "보통", "높음"],
                    key="competition_filter"
                )
            
            # 필터링 적용
            filtered_df = df.copy()
            
            if search_filter:
                filtered_df = filtered_df[filtered_df['keyword'].str.contains(search_filter, case=False, na=False)]
            
            if min_search_volume > 0:
                filtered_df = filtered_df[filtered_df['total_search'] >= min_search_volume]
            
            if competition_filter != "전체":
                filtered_df = filtered_df[filtered_df['competition'] == competition_filter]
            
            # 결과 개수 제한
            if result_limit != "전체":
                filtered_df = filtered_df.head(result_limit)
            
            # 전체 결과 테이블
            st.subheader(f"📋 키워드 분석 결과 ({len(filtered_df)}개)")
            
            if len(filtered_df) != len(df):
                st.info(f"필터 적용 결과: {len(filtered_df)}개 / 전체 {len(df)}개")
            
            # 테이블 스타일링
            styled_df = filtered_df.copy()
            styled_df.index = range(1, len(styled_df) + 1)
            styled_df.columns = ['키워드', 'PC 검색량', '모바일 검색량', '총 검색량', '경쟁도', '데이터 소스']
            
            st.dataframe(
                styled_df,
                use_container_width=True,
                height=500,
                column_config={
                    "PC 검색량": st.column_config.NumberColumn(
                        "PC 검색량",
                        help="PC에서의 월간 검색량",
                        format="%d"
                    ),
                    "모바일 검색량": st.column_config.NumberColumn(
                        "모바일 검색량",
                        help="모바일에서의 월간 검색량",
                        format="%d"
                    ),
                    "총 검색량": st.column_config.NumberColumn(
                        "총 검색량",
                        help="PC + 모바일 총 검색량",
                        format="%d"
                    ),
                    "경쟁도": st.column_config.TextColumn(
                        "경쟁도",
                        help="키워드 광고 경쟁도"
                    )
                }
            )
            
            # 분석 인사이트
            st.subheader("💡 키워드 분석 인사이트")
            
            # 원본 데이터를 사용하여 분석 (컬럼명 변경 전)
            high_volume_keywords = filtered_df[filtered_df['total_search'] > filtered_df['total_search'].quantile(0.7)]
            low_competition_keywords = filtered_df[filtered_df['competition'] == '낮음']
            
            col_insight1, col_insight2 = st.columns(2)
            
            with col_insight1:
                st.info(f"""
                **검색량 분석:**
                - 총 키워드: {len(filtered_df)}개
                - 고검색량 키워드: {len(high_volume_keywords)}개
                - 평균 검색량: {int(filtered_df['total_search'].mean()):,}
                - 최고 검색량: {int(filtered_df['total_search'].max()):,}
                """)
            
            with col_insight2:
                st.success(f"""
                **마케팅 기회:**
                - 저경쟁 키워드: {len(low_competition_keywords)}개
                - 추천 타겟 키워드: 고검색량 + 저경쟁
                - 롱테일 키워드 활용 권장
                """)
            
            # 추천 키워드 (고검색량 + 저경쟁)
            recommended_keywords = filtered_df[
                (filtered_df['total_search'] > filtered_df['total_search'].median()) & 
                (filtered_df['competition'].isin(['낮음', '보통']))
            ].head(10)
            
            if len(recommended_keywords) > 0:
                st.subheader("🎯 추천 타겟 키워드")
                st.success("검색량이 높고 경쟁도가 상대적으로 낮은 키워드들입니다.")
                
                for idx, row in recommended_keywords.iterrows():
                    with st.container():
                        col_rec1, col_rec2, col_rec3, col_rec4 = st.columns([2, 1, 1, 1])
                        with col_rec1:
                            st.write(f"**{row['keyword']}**")
                        with col_rec2:
                            st.write(f"검색량: {int(row['total_search']):,}")
                        with col_rec3:
                            st.write(f"경쟁도: {row['competition']}")
                        with col_rec4:
                            if row['competition'] == '낮음':
                                st.success("🎯 추천")
                            else:
                                st.info("📊 고려")
            
            # CSV 다운로드
            st.subheader("📥 데이터 저장")
            col_download1, col_download2 = st.columns(2)
            
            with col_download1:
                # 현재 필터된 결과 다운로드
                download_df = styled_df.copy()
                csv_data = download_df.to_csv(index=True, encoding='utf-8-sig')
                
                st.download_button(
                    label=f"📥 필터된 결과 CSV 다운로드 ({len(download_df)}개)",
                    data=csv_data,
                    file_name=f"{base_keyword}_연관키워드_필터_{time.strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col_download2:
                # 전체 데이터 다운로드
                full_df = df.copy()
                full_df.index = range(1, len(full_df) + 1)
                full_df.columns = ['키워드', 'PC 검색량', '모바일 검색량', '총 검색량', '경쟁도', '데이터 소스']
                full_csv_data = full_df.to_csv(index=True, encoding='utf-8-sig')
                
                st.download_button(
                    label=f"📥 전체 결과 CSV 다운로드 ({len(df)}개)",
                    data=full_csv_data,
                    file_name=f"{base_keyword}_연관키워드_전체_{time.strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            # 키워드 클라우드
            st.subheader("☁️ 키워드 클라우드")
            top_20_keywords = [kw['keyword'] for kw in related_keywords[:20]]
            keywords_text = " • ".join(top_20_keywords)
            st.markdown(f"**{keywords_text}**")
            
        else:
            st.warning("❌ 연관 키워드를 찾을 수 없습니다. 다른 키워드로 시도해보세요.")
            
            st.subheader("🔍 검색 결과 개선 제안")
            st.info("""
            **결과가 없는 경우 해결 방법:**
            1. **키워드 변경**: 더 일반적이거나 구체적인 키워드 시도
            2. **검색어 확인**: 오타나 띄어쓰기 확인
            3. **관련 키워드**: 유사한 의미의 다른 키워드 시도
            4. **카테고리 확장**: 더 넓은 카테고리의 키워드 고려
            """)

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
            연관 키워드 분석 페이지 - 네이버 검색광고 API 전용
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