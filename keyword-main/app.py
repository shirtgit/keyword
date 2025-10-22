"""
본 프로그램 'RankChecker by 쇼쇼'는 쇼쇼에 의해 개발된 소프트웨어입니다.
해당 소스코드 및 실행 파일의 무단 복제, 배포, 역컴파일, 수정은
저작권법 및 컴퓨터프로그램 보호법에 따라 엄격히 금지됩니다.

무단 유포 및 상업적 이용 시 민형사상 법적 책임을 물을 수 있습니다.

Copyright ⓒ 2025 쇼쇼. All rights reserved.
Unauthorized reproduction or redistribution is strictly prohibited. 
"""

import streamlit as st
import pandas as pd
import os
import json
import urllib.request
import urllib.parse
import re
import time
import hashlib
import hmac
import base64
from collections import Counter
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# 네이버 개발자 API
client_id = os.getenv("NAVER_CLIENT_ID", "RMAReoKGgZ73JCL3AdhK")
client_secret = os.getenv("NAVER_CLIENT_SECRET", "SZS7VRIQDT")

# 네이버 광고센터 API (필요시 사용)
CUSTOMER_ID = os.getenv("CUSTOMER_ID")
ACCESS_LICENSE = os.getenv("ACCESS_LICENSE")
SECRET_KEY = os.getenv("SECRET_KEY")

def get_top_ranked_product_by_mall(keyword, mall_name):
    """네이버 쇼핑에서 특정 키워드로 검색하여 지정된 판매처의 최고 순위 상품을 찾는 함수"""
    encText = urllib.parse.quote(keyword)
    seen_titles = set()
    best_product = None
    
    for start in range(1, 1001, 100):
        url = f"https://openapi.naver.com/v1/search/shop.json?query={encText}&display=100&start={start}"
        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", client_id)
        request.add_header("X-Naver-Client-Secret", client_secret)
        
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

def get_signature(method, uri, timestamp, access_key, secret_key):
    """네이버 검색광고 API 인증을 위한 서명 생성"""
    message = f"{timestamp}.{method}.{uri}"
    signature = base64.b64encode(
        hmac.new(secret_key.encode(), message.encode(), hashlib.sha256).digest()
    ).decode()
    return signature

def get_related_keywords_from_ads_api(keyword):
    """네이버 검색광고 API를 사용하여 연관 키워드 추출"""
    try:
        # API 설정
        BASE_URL = "https://api.naver.com"
        API_PATH = "/keywordstool"
        METHOD = "GET"
        
        # 인증 정보
        access_license = ACCESS_LICENSE
        secret_key = SECRET_KEY
        customer_id = CUSTOMER_ID
        
        if not all([access_license, secret_key, customer_id]):
            st.error("❌ 네이버 검색광고 API 설정이 필요합니다.")
            return []
        
        # 타임스탬프 생성
        timestamp = str(int(time.time() * 1000))
        
        # 서명 생성
        signature = get_signature(METHOD, API_PATH, timestamp, access_license, secret_key)
        
        # 헤더 설정
        headers = {
            "X-Timestamp": timestamp,
            "X-API-KEY": access_license,
            "X-Customer": customer_id,
            "X-Signature": signature,
            "Content-Type": "application/json"
        }
        
        # GET 방식으로 쿼리 파라미터 전송
        query_params = urllib.parse.urlencode({
            'hintKeywords': keyword,
            'showDetail': '1'
        })
        url = f"{BASE_URL}{API_PATH}?{query_params}"
        request = urllib.request.Request(url, headers=headers, method=METHOD)
        
        with urllib.request.urlopen(request) as response:
            result = json.loads(response.read().decode('utf-8'))
            
        # 결과 처리
        related_keywords = []
        if 'keywordList' in result:
            for item in result['keywordList']:
                # 검색량 처리 (문자열인 경우 0으로 처리)
                pc_qc = item.get('monthlyPcQcCnt', 0)
                mobile_qc = item.get('monthlyMobileQcCnt', 0)
                
                # "< 10" 같은 문자열 처리
                if isinstance(pc_qc, str):
                    pc_qc = 5 if "< 10" in pc_qc else 0
                if isinstance(mobile_qc, str):
                    mobile_qc = 5 if "< 10" in mobile_qc else 0
                
                related_keywords.append({
                    'keyword': item.get('relKeyword', ''),
                    'monthly_pc_qc': pc_qc,
                    'monthly_mobile_qc': mobile_qc,
                    'competition': item.get('compIdx', 'N/A'),
                    'source': 'ads_api'
                })
        
        return related_keywords
        
    except Exception as e:
        st.error(f"❌ 검색광고 API 오류: {e}")
        return []

def get_shopping_related_keywords(keyword):
    """네이버 쇼핑 API에서 연관 키워드를 추출하는 함수"""
    encText = urllib.parse.quote(keyword)
    related_keywords = []
    all_data = []
    
    try:
        progress_placeholder = st.empty()
        
        # 다양한 정렬 방식으로 검색
        sort_options = ["sim", "date", "asc", "dsc"]
        
        for sort_type in sort_options:
            for start in range(1, 301, 100):  # 각 정렬별로 3페이지씩
                try:
                    url = f"https://openapi.naver.com/v1/search/shop.json?query={encText}&display=100&start={start}&sort={sort_type}"
                    request = urllib.request.Request(url)
                    request.add_header("X-Naver-Client-Id", client_id)
                    request.add_header("X-Naver-Client-Secret", client_secret)
                    
                    response = urllib.request.urlopen(request)
                    result = json.loads(response.read())
                    
                    items = result.get("items", [])
                    if not items:
                        break
                    
                    for item in items:
                        title_clean = re.sub(r"<.*?>", "", item.get("title", ""))
                        category = item.get("category1", "") + " " + item.get("category2", "") + " " + item.get("category3", "") + " " + item.get("category4", "")
                        brand = item.get("brand", "")
                        mall = item.get("mallName", "")
                        
                        combined_text = f"{title_clean} {category} {brand} {mall}".strip()
                        if combined_text:
                            all_data.append(combined_text)
                    
                    current_count = len(all_data)
                    progress_placeholder.text(f"📊 수집된 상품 데이터: {current_count}개 (정렬: {sort_type})")
                    
                    time.sleep(0.03)
                    
                except Exception as api_error:
                    continue
        
        progress_placeholder.text(f"✅ 총 {len(all_data)}개 상품 데이터 수집 완료!")
        
        if not all_data:
            return []
        
        # 키워드 추출
        all_words = []
        for text in all_data:
            basic_words = re.findall(r'[가-힣a-zA-Z0-9]+', text)
            phrases = re.findall(r'[가-힣a-zA-Z0-9\s]{2,20}', text)
            clean_phrases = [phrase.strip() for phrase in phrases if len(phrase.strip()) >= 2]
            unit_words = re.findall(r'\d+[가-힣a-zA-Z]+', text)
            
            extracted_words = basic_words + clean_phrases + unit_words
            filtered_words = [word for word in extracted_words if 2 <= len(word) <= 30]
            all_words.extend(filtered_words)
        
        word_counts = Counter(all_words)
        
        exclude_words = {
            keyword.lower(), '상품', '제품', '브랜드', '공식', '정품', '무료', '배송', 
            '할인', '세트', '특가', '이벤트', '쿠폰', '적립', '포인트', '원', '개', '매',
            '구매', '판매', '스토어', '쇼핑', '마트', '몰', '샵', '온라인', '오프라인',
            '신상', '신제품', '런칭', '출시', '한정', '단독', '독점', '전용', '추천',
            '베스트', '인기', '랭킹', '순위', 'top', 'best', '당일', '오늘', '내일',
            '빠른', '즉시', '바로', '직접', '직구', '해외', '국내', '한국', '전국',
            '서울', '부산', '대구', '광주', '대전', '울산', '인천', '경기', '강원',
            '리뷰', '후기', '평점', '별점', '만족', '불만', '최고', '최저', '평균'
        }
        
        exclude_patterns = [r'^\d+$', r'^[a-zA-Z]{1}$', r'^.{1}$']
        
        for word, count in word_counts.most_common():
            if (word.lower() not in exclude_words and 
                word.lower() != keyword.lower() and 
                len(word) >= 2 and 
                count >= 1):
                
                exclude = False
                for pattern in exclude_patterns:
                    if re.match(pattern, word):
                        exclude = True
                        break
                
                if not exclude:
                    related_keywords.append({
                        'keyword': word,
                        'frequency': count,
                        'relevance_score': round((count / len(all_data)) * 100, 2),
                        'source': 'shopping_api'
                    })
        
        return related_keywords
        
    except Exception as e:
        st.warning(f"쇼핑 API 오류: {e}")
        return []

def get_related_keywords(keyword):
    """네이버 검색광고 API를 사용하여 연관 키워드 추출"""
    # 네이버 검색광고 API에서 연관 키워드 가져오기
    st.info("🎯 네이버 검색광고 API에서 연관 키워드 수집 중...")
    related_keywords = get_related_keywords_from_ads_api(keyword)
    
    if related_keywords:
        # 검색량 기준으로 정렬
        related_keywords.sort(key=lambda x: (x.get('monthly_pc_qc', 0) + x.get('monthly_mobile_qc', 0)), reverse=True)
        st.success(f"🎉 총 {len(related_keywords)}개의 연관 키워드를 발견했습니다!")
        return related_keywords
    else:
        st.error("❌ 연관 키워드를 찾을 수 없습니다.")
        return []

def render_rank_checker_tab():
    """순위 확인 탭 렌더링"""
    # 사이드바에 정보 표시
    with st.sidebar:
        st.info("### 📊 순위 확인\n1. 검색할 키워드들을 쉼표로 구분하여 입력\n2. 찾을 판매처명 입력\n3. 순위 확인 버튼 클릭")
        st.warning("⚠️ 최대 10개의 키워드까지 검색 가능합니다.")
    
    # 메인 입력 영역
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # 키워드 입력
        keywords_input = st.text_area(
            "검색어 (최대 10개, 쉼표로 구분)",
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
        search_button = st.button("🔍 순위 확인", type="primary", width="stretch", key="rank_search")
    
    with col2:
        st.info("### 💡 팁\n- 정확한 판매처명을 입력하세요\n- 키워드는 구체적으로 입력할수록 정확합니다")
    
    # 검색 실행
    if search_button:
        if not keywords_input.strip() or not mall_name.strip():
            st.error("❌ 검색어와 판매처명을 모두 입력해주세요.")
            return
        
        # 키워드 파싱
        keywords = [k.strip() for k in keywords_input.split(",") if k.strip()]
        
        if len(keywords) > 10:
            st.error("❌ 검색어는 최대 10개까지만 입력 가능합니다.")
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
                    st.link_button("상품보기", product['link'], width="stretch")

def render_related_keywords_tab():
    """연관 키워드 탭 렌더링"""
    # 사이드바에 정보 표시
    with st.sidebar:
        st.info("### 🔗 연관 키워드\n1. 기준이 될 키워드 입력\n2. 연관 키워드 검색 버튼 클릭\n3. 결과를 CSV로 다운로드 가능")
        st.success("🎯 네이버 검색광고 API 사용!")
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
        search_related_button = st.button("🎯 연관 키워드 검색 (검색광고 API)", type="primary", width="stretch", key="related_search")
    
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
                chart_count = min(20, len(df))
                top_keywords = df.head(chart_count)
                
                # 바 차트
                st.bar_chart(data=top_keywords.set_index('keyword')['total_search'])
            
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
                    width="stretch"
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
                    width="stretch"
                )
            
            # 키워드 클라우드 스타일 표시
            st.subheader("☁️ 키워드 클라우드")
            top_20_keywords = [kw['keyword'] for kw in related_keywords[:20]]
            keywords_text = " • ".join(top_20_keywords)
            st.markdown(f"**{keywords_text}**")
            
        else:
            st.warning("❌ 연관 키워드를 찾을 수 없습니다. 다른 키워드로 시도해보세요.")

def main():
    # 페이지 설정
    st.set_page_config(
        page_title="네이버 쇼핑 분석기 (by 쇼쇼)",
        page_icon="🔍",
        layout="wide"
    )
    
    # 헤더
    st.title("🔍 네이버 쇼핑 분석기")
    st.subheader("by 쇼쇼")
    
    # 탭 생성
    tab1, tab2 = st.tabs(["📊 순위 확인", "🔗 연관 키워드"])
    
    with tab1:
        render_rank_checker_tab()
    
    with tab2:
        render_related_keywords_tab()
    
    # 푸터
    st.divider()
    st.markdown(
        """
        <div style='text-align: center; color: gray; font-size: 12px;'>
        ⓒ 2025 쇼쇼. 무단 복제 및 배포 금지. All rights reserved.
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()