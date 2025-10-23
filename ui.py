"""
UI module for the marketing tool
각 탭의 렌더링 함수들과 UI 컴포넌트
"""

import streamlit as st
import pandas as pd
import time
from api import get_top_ranked_product_by_mall, get_related_keywords
from config import AppConfig

def render_rank_checker_tab():
    """순위 확인 탭 렌더링"""
    # 사이드바에 정보 표시
    with st.sidebar:
        st.info("### 📊 순위 확인\n1. 검색할 키워드들을 쉼표로 구분하여 입력\n2. 찾을 판매처명 입력\n3. 순위 확인 버튼 클릭")
        st.warning(f"⚠️ 최대 {AppConfig.MAX_KEYWORDS}개의 키워드까지 검색 가능합니다.")
    
    # 메인 입력 영역
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # 키워드 입력
        keywords_input = st.text_area(
            f"검색어 (최대 {AppConfig.MAX_KEYWORDS}개, 쉼표로 구분)",
            placeholder="예: 키보드, 마우스, 충전기",
            height=100,
            key="rank_keywords"
        )
        
        # 판매처명 입력
        mall_name = st.text_input(
            "판매처명",
            placeholder="예: OO스토어",
            key="rank_mall"
        )
        
        # 검색 버튼
        search_button = st.button("🔍 순위 확인", type="primary", use_container_width=True, key="rank_search")
    
    with col2:
        st.info("### 💡 팁\n- 정확한 판매처명을 입력하세요\n- 키워드는 구체적으로 입력할수록 정확합니다")
    
    # 검색 실행
    if search_button:
        if not keywords_input.strip() or not mall_name.strip():
            st.error("❌ 검색어와 판매처명을 모두 입력해주세요.")
            return
        
        # 키워드 파싱
        keywords = [k.strip() for k in keywords_input.split(",") if k.strip()]
        
        if len(keywords) > AppConfig.MAX_KEYWORDS:
            st.error(f"❌ 검색어는 최대 {AppConfig.MAX_KEYWORDS}개까지만 입력 가능합니다.")
            return
        
        # 검색 시작
        st.success(f"🔄 {len(keywords)}개 키워드로 '{mall_name}' 판매처 검색을 시작합니다...")
        
        results = {}
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # 결과 표시 영역
        results_container = st.container()
        
        for i, keyword in enumerate(keywords):
            status_text.text(f"🔍 '{keyword}' 검색 중... ({i+1}/{len(keywords)})")
            progress_bar.progress((i + 1) / len(keywords))
            
            result = get_top_ranked_product_by_mall(keyword, mall_name)
            results[keyword] = result
            
            # 실시간 결과 표시
            with results_container:
                if result:
                    st.success(f"✅ **{keyword}** → {result['rank']}위 발견!")
                    with st.expander(f"📋 {keyword} 상세 정보", expanded=True):
                        col1, col2, col3 = st.columns([2, 1, 1])
                        with col1:
                            st.write(f"**상품명:** {result['title']}")
                            st.write(f"**판매처:** {result['mallName']}")
                        with col2:
                            st.write(f"**순위:** {result['rank']}위")
                        with col3:
                            st.write(f"**가격:** {int(result['price']):,}원")
                        st.write(f"**링크:** [상품 보기]({result['link']})")
                else:
                    st.warning(f"❌ **{keyword}** → 검색 결과 없음")
            
            # API 호출 간격 조절
            time.sleep(0.1)
        
        # 검색 완료
        status_text.text("✅ 모든 검색이 완료되었습니다!")
        progress_bar.progress(1.0)
        
        # 결과 요약
        st.divider()
        st.subheader("📊 검색 결과 요약")
        
        found_count = sum(1 for result in results.values() if result)
        st.metric("검색된 상품", f"{found_count}/{len(keywords)}")
        
        if found_count > 0:
            # 순위별 정렬
            found_products = [(k, v) for k, v in results.items() if v]
            found_products.sort(key=lambda x: x[1]['rank'])
            
            st.subheader("🏆 순위별 결과")
            for keyword, product in found_products:
                col1, col2, col3, col4 = st.columns([1, 3, 1, 1])
                with col1:
                    st.write(f"**{product['rank']}위**")
                with col2:
                    st.write(f"**{keyword}**")
                with col3:
                    st.write(f"{int(product['price']):,}원")
                with col4:
                    st.link_button("상품보기", product['link'], use_container_width=True)

def render_related_keywords_tab():
    """연관 키워드 탭 렌더링"""
    # 사이드바에 정보 표시
    with st.sidebar:
        st.info("### 🔗 연관 키워드\n1. 기준이 될 키워드 입력\n2. 연관 키워드 검색 버튼 클릭\n3. 결과를 CSV로 다운로드 가능")
        st.success("🎯 네이버 검색광고 API 전용!")
        st.info("📊 공식 검색광고 데이터")
        st.success("✨ 검색량, 경쟁도 정보 제공")
        st.warning("⚠️ 정확한 마케팅 데이터를 제공합니다.")
    
    # 메인 입력 영역
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # 키워드 입력
        base_keyword = st.text_input(
            "기준 키워드",
            placeholder="예: 키보드",
            key="related_keyword"
        )
        
        # 검색 옵션
        st.subheader("🔧 표시 옵션")
        
        show_top_chart = st.checkbox(
            "상위 키워드 차트 표시",
            value=True,
            help="상위 20개 키워드를 차트로 표시"
        )
        
        # 검색 버튼
        search_related_button = st.button("🎯 연관 키워드 검색 (검색광고 API)", type="primary", use_container_width=True, key="related_search")
    
    with col2:
        st.info("### 💡 연관 키워드란?\n- 입력한 키워드와 함께 검색되는 단어들\n- 마케팅 키워드 발굴에 유용\n- 상품명 최적화에 활용 가능")
        st.success("### 🎯 네이버 검색광고 API\n- 🎯 공식 연관 키워드 데이터\n- 📊 정확한 검색량 정보\n- 💡 경쟁도 분석\n- ✨ 마케팅 최적화")
    
    # 검색 실행
    if search_related_button:
        if not base_keyword.strip():
            st.error("❌ 기준 키워드를 입력해주세요.")
            return
        
        st.success(f"🔄 '{base_keyword}' 키워드의 연관 키워드를 검색합니다...")
        
        # 프로그레스 바와 상태 텍스트
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("🎯 네이버 검색광고 API에서 데이터를 수집하는 중...")
        progress_bar.progress(0.5)
        
        # 연관 키워드 검색
        related_keywords = get_related_keywords(base_keyword)
        
        progress_bar.progress(1.0)
        status_text.text("✅ 연관 키워드 검색이 완료되었습니다!")
        
        if related_keywords:
            st.divider()
            st.subheader(f"🔗 '{base_keyword}'의 연관 키워드")
            
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
            
            # 메트릭 표시
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("총 연관 키워드", len(related_keywords))
            with col2:
                st.metric("데이터 소스", "검색광고 API")
            with col3:
                avg_search = df['total_search'].mean()
                st.metric("평균 검색량", f"{int(avg_search):,}")
            with col4:
                total_search = df['total_search'].sum()
                st.metric("총 검색량", f"{int(total_search):,}")
            
            # 상위 키워드를 차트로 표시 (옵션에 따라)
            if show_top_chart:
                st.subheader("📊 상위 연관 키워드")
                chart_count = min(AppConfig.MAX_CHART_ITEMS, len(df))
                top_keywords = df.head(chart_count)
                
                # 개선된 바 차트 (Y축 0 시작, 마우스 휠 비활성화, 가독성 향상)
                import altair as alt
                
                # 최대값 계산 (여유 공간 10% 추가)
                max_value = top_keywords['total_search'].max()
                y_max = int(max_value * 1.1) if max_value > 0 else 100
                
                # Altair 차트 생성
                chart = alt.Chart(top_keywords).mark_bar(
                    color='steelblue',
                    opacity=0.8
                ).add_selection(
                    alt.selection_single()
                ).encode(
                    x=alt.X(
                        'total_search:Q', 
                        title='총 검색량',
                        scale=alt.Scale(domain=[0, y_max]),  # Y축 0부터 최대값+10%까지
                        axis=alt.Axis(format=',.0f')  # 정수로 반올림 + 천단위 콤마 표시
                    ),
                    y=alt.Y(
                        'keyword:N', 
                        sort='-x', 
                        title='키워드',
                        axis=alt.Axis(labelLimit=150)  # 긴 키워드명 처리
                    ),
                    tooltip=[
                        alt.Tooltip('keyword:N', title='키워드'),
                        alt.Tooltip('total_search:Q', title='총 검색량', format=',.0f'),
                        alt.Tooltip('pc_search:Q', title='PC 검색량', format=',.0f'),
                        alt.Tooltip('mobile_search:Q', title='모바일 검색량', format=',.0f')
                    ]
                ).properties(
                    height=400,
                    title=alt.TitleParams(
                        text="상위 연관 키워드 검색량 (검색광고 API)",
                        fontSize=16,
                        anchor='start'
                    )
                ).configure_axis(
                    labelFontSize=11,
                    titleFontSize=12
                ).configure_title(
                    fontSize=16,
                    color='#2c3e50'
                ).resolve_scale(
                    color='independent'
                )
                
                # 마우스 휠 비활성화 CSS
                st.markdown(
                    """
                    <style>
                    .stPlotlyChart > div {
                        pointer-events: none;
                    }
                    div[data-testid="stVegaLiteChart"] > div {
                        pointer-events: none !important;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True
                )
                
                # 차트 표시
                st.altair_chart(chart, use_container_width=True)
            
            # 전체 결과 테이블
            st.subheader(f"📋 전체 연관 키워드 목록 ({len(df)}개)")
            
            # 검색 및 필터링 옵션
            col_filter1, col_filter2, col_filter3 = st.columns(3)
            
            with col_filter1:
                search_filter = st.text_input(
                    "🔍 키워드 검색 필터",
                    placeholder="특정 키워드 검색...",
                    key="keyword_filter"
                )
            
            with col_filter2:
                sort_option = st.selectbox(
                    "📊 정렬 기준",
                    options=["검색량순", "키워드명순", "데이터소스순"],
                    key="sort_option"
                )
            
            with col_filter3:
                source_filter = st.selectbox(
                    "📡 데이터 소스",
                    options=["전체", "검색광고 API", "쇼핑 API"],
                    key="source_filter"
                )
            
            # 필터링 적용
            filtered_df = df.copy()
            if search_filter:
                filtered_df = filtered_df[filtered_df['keyword'].str.contains(search_filter, case=False, na=False)]
            
            if source_filter != "전체":
                filtered_df = filtered_df[filtered_df['source'] == source_filter]
            
            # 정렬 적용
            if sort_option == "검색량순":
                filtered_df = filtered_df.sort_values('total_search', ascending=False)
            elif sort_option == "키워드명순":
                filtered_df = filtered_df.sort_values('keyword')
            else:  # 데이터소스순
                filtered_df = filtered_df.sort_values('source')
            
            # 테이블 스타일링
            styled_df = filtered_df.copy()
            styled_df.index = range(1, len(styled_df) + 1)
            styled_df.columns = ['키워드', 'PC 검색량', '모바일 검색량', '총 검색량', '경쟁도', '데이터 소스']
            
            # 결과 개수 표시
            if len(filtered_df) != len(df):
                st.info(f"필터 적용 결과: {len(filtered_df)}개 / 전체 {len(df)}개")
            
            # 페이지네이션을 위한 옵션
            if len(styled_df) > 100:
                show_all = st.checkbox("📊 모든 결과 표시 (성능에 영향을 줄 수 있음)", value=False)
                if not show_all:
                    styled_df = styled_df.head(100)
                    st.warning(f"⚠️ 성능을 위해 상위 100개만 표시합니다. 전체 보기를 원하시면 위 체크박스를 선택하세요.")
            
            st.dataframe(
                styled_df,
                use_container_width=True,
                height=400,
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
                        help="PC + 모바일 총 검색량 또는 쇼핑 API 빈도",
                        format="%d"
                    )
                }
            )
            
            # CSV 다운로드 버튼
            col_download1, col_download2 = st.columns(2)
            with col_download1:
                download_df = filtered_df.copy()
                download_df.index = range(1, len(download_df) + 1)
                download_df.columns = ['키워드', 'PC 검색량', '모바일 검색량', '총 검색량', '경쟁도', '데이터 소스']
                csv_data = download_df.to_csv(index=True, encoding='utf-8-sig')
                
                st.download_button(
                    label=f"📥 현재 결과 CSV 다운로드 ({len(download_df)}개)",
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
            
            # 키워드 클라우드 스타일 표시
            st.subheader("☁️ 키워드 클라우드")
            top_20_keywords = [kw['keyword'] for kw in related_keywords[:20]]
            keywords_text = " • ".join(top_20_keywords)
            st.markdown(f"**{keywords_text}**")
            
        else:
            st.warning("❌ 연관 키워드를 찾을 수 없습니다. 다른 키워드로 시도해보세요.")

def render_dashboard_metrics():
    """대시보드 메트릭 렌더링"""
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🎯 활성 API", "검색광고 API", "정상 작동")
    with col2:
        st.metric("📊 지원 기능", "2개", "순위 확인 + 키워드 분석")
    with col3:
        st.metric("🔍 분석 범위", "네이버 쇼핑", "전체 상품")
    with col4:
        st.metric("⚡ 응답 속도", "실시간", "빠른 분석")

def render_footer():
    """푸터 렌더링"""
    st.divider()
    st.markdown(
        f"""
        <div style='text-align: center; color: gray; font-size: 12px;'>
        {AppConfig.COPYRIGHT_TEXT}<br>
        Professional Marketing Tool - Authorized User Only
        </div>
        """,
        unsafe_allow_html=True
    )