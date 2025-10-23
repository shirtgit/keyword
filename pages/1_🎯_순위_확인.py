"""
순위 확인 페이지
네이버 쇼핑 API를 활용한 키워드별 판매처 순위 확인
"""

import streamlit as st
import pandas as pd
import time
from api import get_top_ranked_product_by_mall
from config import AppConfig
from auth import initialize_session, is_logged_in, render_logout_section

def render_navigation_sidebar():
    """사이드바 네비게이션 렌더링"""
    with st.sidebar:
        st.markdown("### 🧭 페이지 네비게이션")
        
        # 현재 페이지 표시
        current_page = "🎯 순위 확인"
        st.info(f"현재 페이지: **{current_page}**")
        
        st.markdown("---")
        
        # 페이지 링크들
        st.markdown("### 📋 메뉴")
        
        if st.button("🏠 홈 대시보드", use_container_width=True):
            st.switch_page("app.py")
        
        if st.button("🎯 순위 확인", use_container_width=True, disabled=True):
            st.switch_page("pages/1_🎯_순위_확인.py")
        
        if st.button("🔗 연관 키워드", use_container_width=True):
            st.switch_page("pages/2_🔗_연관_키워드.py")
        
        if st.button("📊 키워드 상세 분석", use_container_width=True):
            st.switch_page("pages/4_📊_키워드_상세_분석.py")
        
        if st.button("⚙️ 설정", use_container_width=True):
            st.switch_page("pages/3_⚙️_설정.py")
        
        st.markdown("---")
        
        # 현재 페이지 기능 설명
        st.markdown("### 🎯 순위 확인 기능")
        st.markdown("""
        - 네이버 쇼핑 API 활용
        - 키워드별 판매처 순위 확인
        - 실시간 데이터 수집
        - 최대 10개 키워드 동시 검색
        """)
        
        # 사용자 정보
        current_user = st.session_state.get('username', 'Unknown')
        st.markdown(f"### 👤 사용자: **{current_user}**")

def render_rank_checker_page():
    """순위 확인 페이지 렌더링"""
    # 다크모드/라이트모드 대응 CSS
    st.markdown("""
    <style>
    /* 컨테이너 최적화 */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 1200px;
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
    
    /* 텍스트 영역 높이 조정 */
    .stTextArea textarea {
        min-height: 80px !important;
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
        <h1 class="page-title">🎯 순위 확인</h1>
        <p class="page-subtitle">네이버 쇼핑에서 키워드별 판매처 순위를 실시간으로 확인하세요</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 로그아웃 섹션을 우상단에 배치
    col_spacer, col_logout = st.columns([4, 1])
    with col_logout:
        render_logout_section()
    

    
    # 메인 입력 영역
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # 키워드 입력
        keywords_input = st.text_area(
            "🔍 검색 키워드",
            placeholder="키워드, 마우스, 충전기",
            height=100,
            key="rank_keywords"
        )
        
        # 판매처명 입력
        mall_name = st.text_input(
            "🏪 판매처명",
            placeholder="쿠팡",
            key="rank_mall"
        )
        
        # 검색 옵션
        show_details = st.checkbox("📋 상세 정보 표시", value=True)
        
        # 검색 버튼
        search_button = st.button(
            "🔍 순위 확인", 
            type="primary", 
            use_container_width=True, 
            key="rank_search"
        )
    
    with col2:
        st.info(f"**최대 {AppConfig.MAX_KEYWORDS}개 키워드**\n쉼표로 구분하여 입력")
    
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
                    
                    if show_details:
                        with st.expander(f"📋 {keyword} 상세 정보", expanded=True):
                            col_detail1, col_detail2, col_detail3 = st.columns([2, 1, 1])
                            with col_detail1:
                                st.write(f"**상품명:** {result['title']}")
                                st.write(f"**판매처:** {result['mallName']}")
                            with col_detail2:
                                st.metric("순위", f"{result['rank']}위")
                            with col_detail3:
                                st.metric("가격", f"{int(result['price']):,}원")
                            
                            col_link1, col_link2 = st.columns([1, 1])
                            with col_link1:
                                st.link_button("🛒 상품 페이지", result['link'], use_container_width=True)
                            with col_link2:
                                st.write(f"**카테고리:** {result.get('category1', 'N/A')}")
                else:
                    st.warning(f"❌ **{keyword}** → '{mall_name}' 판매처에서 검색 결과 없음")
            
            # API 호출 간격 조절
            time.sleep(0.2)
        
        # 검색 완료
        status_text.text("✅ 모든 검색이 완료되었습니다!")
        progress_bar.progress(1.0)
        
        # 결과 요약 및 분석
        st.markdown("---")
        st.subheader("📊 검색 결과 분석")
        
        found_count = sum(1 for result in results.values() if result)
        not_found_count = len(keywords) - found_count
        
        # 메트릭 표시
        col_metric1, col_metric2, col_metric3, col_metric4 = st.columns(4)
        with col_metric1:
            st.metric("총 검색 키워드", len(keywords))
        with col_metric2:
            st.metric("검색 성공", found_count, delta=f"+{found_count}")
        with col_metric3:
            st.metric("검색 실패", not_found_count, delta=f"-{not_found_count}" if not_found_count > 0 else None)
        with col_metric4:
            success_rate = (found_count / len(keywords)) * 100 if keywords else 0
            st.metric("성공률", f"{success_rate:.1f}%")
        
        if found_count > 0:
            # 순위별 정렬된 결과 표시
            st.subheader("🏆 순위별 검색 결과")
            found_products = [(k, v) for k, v in results.items() if v]
            found_products.sort(key=lambda x: x[1]['rank'])
            
            # 순위 차트 데이터 준비
            chart_data = []
            for keyword, product in found_products:
                chart_data.append({
                    'keyword': keyword,
                    'rank': product['rank'],
                    'price': int(product['price'])
                })
            
            df_chart = pd.DataFrame(chart_data)
            
            # 순위 차트 표시
            if len(df_chart) > 1:
                st.subheader("📈 순위 시각화")
                
                # Altair 차트 생성
                import altair as alt
                
                chart = alt.Chart(df_chart).mark_bar(
                    color='steelblue',
                    opacity=0.8
                ).encode(
                    x=alt.X('keyword:N', title='키워드', sort=alt.Sort(field='rank', order='ascending')),
                    y=alt.Y('rank:Q', title='순위 (낮을수록 좋음)', scale=alt.Scale(reverse=True)),
                    tooltip=[
                        alt.Tooltip('keyword:N', title='키워드'),
                        alt.Tooltip('rank:Q', title='순위'),
                        alt.Tooltip('price:Q', title='가격', format=',.0f')
                    ]
                ).properties(
                    height=300,
                    title=alt.TitleParams(
                        text=f"'{mall_name}' 판매처의 키워드별 순위",
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
                
                st.altair_chart(chart, use_container_width=True)
            
            # 상세 테이블
            st.subheader("📋 상세 결과 테이블")
            table_data = []
            for keyword, product in found_products:
                table_data.append({
                    '키워드': keyword,
                    '순위': f"{product['rank']}위",
                    '상품명': product['title'][:50] + "..." if len(product['title']) > 50 else product['title'],
                    '판매처': product['mallName'],
                    '가격': f"{int(product['price']):,}원",
                    '링크': product['link']
                })
            
            df_table = pd.DataFrame(table_data)
            df_table.index = range(1, len(df_table) + 1)
            
            st.dataframe(
                df_table,
                use_container_width=True,
                column_config={
                    "링크": st.column_config.LinkColumn(
                        "상품 링크",
                        help="클릭하면 해당 상품 페이지로 이동합니다",
                        display_text="🛒 상품보기"
                    )
                }
            )
            
            # CSV 다운로드
            csv_data = df_table.to_csv(index=True, encoding='utf-8-sig')
            st.download_button(
                label=f"📥 결과 CSV 다운로드 ({len(df_table)}개)",
                data=csv_data,
                file_name=f"{mall_name}_순위결과_{time.strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
            
            # 분석 인사이트
            st.subheader("💡 분석 인사이트")
            
            best_rank = min(product['rank'] for _, product in found_products)
            worst_rank = max(product['rank'] for _, product in found_products)
            avg_rank = sum(product['rank'] for _, product in found_products) / len(found_products)
            
            col_insight1, col_insight2 = st.columns(2)
            with col_insight1:
                st.info(f"""
                **순위 분석:**
                - 최고 순위: {best_rank}위
                - 최저 순위: {worst_rank}위  
                - 평균 순위: {avg_rank:.1f}위
                """)
            
            with col_insight2:
                if best_rank <= 5:
                    st.success("🎉 상위권 진입 키워드가 있습니다!")
                elif best_rank <= 20:
                    st.warning("⚠️ 중간 순위에 위치합니다. 최적화가 필요할 수 있습니다.")
                else:
                    st.error("📈 순위 개선이 필요합니다. 키워드 최적화를 고려하세요.")
        
        else:
            st.warning("❌ 검색된 상품이 없습니다. 다른 키워드나 판매처명으로 시도해보세요.")
            
            st.subheader("🔍 검색 결과 개선 제안")
            st.info("""
            **검색 결과가 없는 경우 해결 방법:**
            1. **판매처명 확인**: 정확한 쇼핑몰 이름인지 확인
            2. **키워드 수정**: 더 일반적이거나 구체적인 키워드 시도
            3. **띄어쓰기 확인**: 판매처명의 띄어쓰기나 특수문자 확인
            4. **다른 판매처**: 해당 판매처에서 실제로 판매하는지 확인
            """)

def main():
    """순위 확인 페이지 메인"""
    # 페이지 설정
    st.set_page_config(
        page_title="순위 확인 - " + AppConfig.APP_TITLE,
        page_icon="🎯",
        layout=AppConfig.LAYOUT,
        initial_sidebar_state="expanded"
    )
    
    # 세션 초기화
    initialize_session()
    
    # 인증 확인
    if is_logged_in():
        render_rank_checker_page()
        
        # 푸터
        st.markdown("---")
        st.markdown(
            f"""
            <div style='text-align: center; color: gray; font-size: 12px;'>
            {AppConfig.COPYRIGHT_TEXT}<br>
            순위 확인 페이지 - 네이버 쇼핑 API 활용
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