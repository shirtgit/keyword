"""
글 재작성 페이지 - Gemini API 활용
전문적인 카피라이팅을 위한 AI 글 재작성 도구
"""

import streamlit as st
import google.generativeai as genai
import time
import re
from config import APIConfig, AppConfig, AuthConfig
from auth import initialize_session, is_logged_in, render_logout_section, logout_user

def render_navigation_sidebar():
    """사이드바 네비게이션 렌더링"""
    with st.sidebar:
        st.markdown("### 🧭 페이지 네비게이션")
        
        # 현재 페이지 표시
        current_page = "✍️ 글 재작성"
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
        
        if st.button("✍️ 글 재작성", use_container_width=True, disabled=True):
            st.switch_page("pages/5_✍️_글_재작성.py")
        
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
            if st.button("✍️", help="글 재작성 바로가기"):
                st.switch_page("pages/5_✍️_글_재작성.py")
        
        st.markdown("---")
        
        # 시스템 상태
        st.markdown("### 🔧 시스템 상태")
        st.success("🟢 모든 시스템 정상")
        st.info("🤖 Gemini AI 연결됨")
        
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

def initialize_gemini():
    """Gemini API 초기화"""
    try:
        genai.configure(api_key=APIConfig.GEMINI_API_KEY)
        return True
    except Exception as e:
        st.error(f"Gemini API 초기화 실패: {str(e)}")
        return False

def count_characters(text):
    """글자 수 계산 (공백, 이모지 제외)"""
    # 이모지 제거 패턴
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002500-\U00002BEF"  # chinese char
        u"\U00002702-\U000027B0"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U00010000-\U0010ffff"
        u"\u2640-\u2642" 
        u"\u2600-\u2B55"
        u"\u200d"
        u"\u23cf"
        u"\u23e9"
        u"\u231a"
        u"\ufe0f"  # dingbats
        u"\u3030"
    "]+", re.UNICODE)
    
    # 이모지와 공백 제거
    clean_text = emoji_pattern.sub(r'', text)
    clean_text = clean_text.replace(' ', '').replace('\n', '').replace('\t', '')
    
    return len(clean_text)

def rewrite_content(original_text, mode="일반"):
    """Gemini API를 사용하여 글 재작성"""
    try:
        model = genai.GenerativeModel('gemini-2.5-pro')
        
        if mode == "일반":
            prompt = f"""
당신은 전문 카피라이터입니다. 다음 지침에 따라 글을 재작성해주세요:

**필수 조건:**
- 2500자 이상 (공백제외, 이모지제외)
- 전문적이고 자연스러운 사람이 작성한 형태
- 유사문서 검색에 걸리지 않도록 완전히 새로운 표현으로 작성
- 원본의 핵심 내용과 의도는 유지하되 표현을 완전히 바꿔주세요
- 제목을 따로 제공해주세요

**글쓰기 지침:**
- 어투: 전문적이면서 소개하는, 친절한 말투를 사용해주세요
- 구조: 소제목을 붙여 문단별로 체계적으로 작성해주세요
- 문체: 독자에게 정보를 친근하게 전달하는 안내자 역할로 작성
- 톤앤매너: 신뢰감 있으면서도 접근하기 쉬운 전문가 톤
- 문단 구성: 각 소제목 하에 충분한 내용으로 구성 (최소 200-300자씩)

**중요한 출력 규칙:**
- 제목과 본문 외에는 절대 다른 내용을 추가하지 마세요
- 설명, 부연설명, 메타데이터, 주석, 참고사항 등 일체 금지
- 순수하게 제목과 본문 내용만 출력하세요

**원본 글:**
{original_text}

**응답 형식 (이 형식을 정확히 지켜주세요):**
제목: [새로운 제목]

본문:
## 첫 번째 소제목
[해당 내용...]

## 두 번째 소제목  
[해당 내용...]

## 세 번째 소제목
[해당 내용...]

(소제목과 내용을 적절히 구성하여 2500자 이상 작성)
"""
        else:  # HTML 모드
            prompt = f"""
당신은 전문 카피라이터이자 웹 디자이너입니다. 다음 지침에 따라 HTML 형태로 글을 재작성해주세요:

**필수 조건:**
- 2500자 이상 (공백제외, 이모지제외)
- HTML body 안의 내용만 작성
- 모든 CSS는 인라인 스타일로 작성 (예: <p style="color: blue;">)
- 매번 다른 UI 디자인으로 형식 변경
- 전문적이고 자연스러운 사람이 작성한 형태
- 유사문서 검색에 걸리지 않도록 완전히 새로운 표현으로 작성
- 다양한 HTML 요소 활용 (div, section, article, header, p, h1-h6, ul, ol, blockquote 등)
- 아름다운 색상과 레이아웃 적용

**글쓰기 지침:**
- 어투: 전문적이면서 소개하는, 친절한 말투를 사용해주세요
- 구조: HTML 헤딩 태그(h2, h3)로 소제목을 만들어 문단별로 체계적으로 작성
- 문체: 독자에게 정보를 친근하게 전달하는 안내자 역할로 작성
- 톤앤매너: 신뢰감 있으면서도 접근하기 쉬운 전문가 톤
- HTML 구성: section/article 태그로 논리적 구조화, 각 섹션별 충분한 내용
- 시각적 요소: 박스, 강조, 목록 등을 활용하여 가독성 향상

**중요한 출력 규칙:**
- 제목과 HTML 본문 외에는 절대 다른 내용을 추가하지 마세요
- 설명, 부연설명, 메타데이터, 주석, 참고사항 등 일체 금지
- 순수하게 제목과 HTML 본문만 출력하세요

**원본 글:**
{original_text}

**응답 형식 (이 형식을 정확히 지켜주세요):**
제목: [새로운 제목]

HTML:
<article style="max-width: 800px; margin: 0 auto; padding: 20px; font-family: 'Segoe UI', sans-serif;">
    <header style="margin-bottom: 30px;">
        <h1 style="color: #2c3e50; font-size: 28px;">[메인 제목]</h1>
    </header>
    
    <section style="margin-bottom: 25px;">
        <h2 style="color: #34495e; font-size: 22px; margin-bottom: 15px;">[소제목1]</h2>
        <p style="line-height: 1.6; color: #2c3e50;">[내용...]</p>
    </section>
    
    <section style="margin-bottom: 25px;">
        <h2 style="color: #34495e; font-size: 22px; margin-bottom: 15px;">[소제목2]</h2>
        <p style="line-height: 1.6; color: #2c3e50;">[내용...]</p>
    </section>
    
    <!-- 추가 섹션들로 2500자 이상 구성 -->
</article>
"""
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        st.error(f"글 재작성 중 오류 발생: {str(e)}")
        return None

def render_content_rewriter_page():
    """글 재작성 페이지 렌더링"""
    # 민트 테마 CSS
    st.markdown("""
    <style>
    .main .block-container {
        padding-top: 2rem;
        max-width: 1200px;
    }
    
    .rewriter-header {
        background: linear-gradient(135deg, #20B2AA, #48D1CC);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(32, 178, 170, 0.3);
        text-align: center;
    }
    
    .rewriter-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .rewriter-subtitle {
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    
    .stats-container {
        background: rgba(32, 178, 170, 0.1);
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        border: 1px solid rgba(32, 178, 170, 0.3);
    }
    
    .result-container {
        background: #ffffff;
        color: #333333;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.1);
        border: 1px solid rgba(32, 178, 170, 0.2);
        margin-top: 1rem;
        line-height: 1.6;
        font-size: 14px;
    }
    
    .result-container p, .result-container div, .result-container span {
        color: #333333 !important;
    }
    
    /* 다크모드 대응 */
    @media (prefers-color-scheme: dark) {
        .result-container {
            background: #2d2d2d !important;
            color: #e0e0e0 !important;
        }
        .result-container p, .result-container div, .result-container span {
            color: #e0e0e0 !important;
        }
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #20B2AA, #48D1CC) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 6px rgba(32, 178, 170, 0.3) !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #48D1CC, #40E0D0) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 10px rgba(32, 178, 170, 0.4) !important;
    }
    
    .stTextArea > div > div > textarea {
        border-radius: 8px !important;
        border: 2px solid rgba(32, 178, 170, 0.3) !important;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #20B2AA !important;
        box-shadow: 0 0 5px rgba(32, 178, 170, 0.5) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 사이드바 네비게이션
    render_navigation_sidebar()
    
    # 가운데 정렬된 헤더
    st.markdown("""
    <div class="rewriter-header">
        <h1 class="rewriter-title">✍️ AI 글 재작성</h1>
        <p class="rewriter-subtitle">Gemini AI로 전문적인 카피라이팅을 경험하세요</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 기능 설명
    st.info("""
    ### 🎯 AI 글 재작성 기능
    - **Google Gemini AI** 활용 - 최신 생성형 AI 기술
    - **2500자 이상** 전문적인 글 생성
    - **유사문서 회피** - 완전히 새로운 표현으로 재작성
    - **전문적 어투** - 친절하고 소개하는 말투로 작성
    - **체계적 구조** - 소제목별 문단 구성으로 가독성 향상
    - **순수 콘텐츠** - 제목과 본문 외 불필요한 내용 제거
    - **HTML 모드** - 웹사이트용 스타일링된 콘텐츠 생성
    - **실시간 글자수 체크** - 공백/이모지 제외 정확한 카운팅
    """)
    
    # Gemini API 초기화
    if 'gemini_initialized' not in st.session_state:
        st.session_state.gemini_initialized = initialize_gemini()
    
    if not st.session_state.gemini_initialized:
        st.error("Gemini API 연결에 실패했습니다. 관리자에게 문의하세요.")
        return
    
    # 입력 영역
    st.markdown("### 📝 원본 글 입력")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        original_text = st.text_area(
            "재작성할 원본 글을 입력하세요:",
            height=300,
            placeholder="여기에 재작성할 글을 입력하세요...\n\n예시:\n- 블로그 포스트\n- 마케팅 카피\n- 상품 설명\n- 기업 소개글\n등 모든 종류의 텍스트를 전문적으로 재작성합니다."
        )
    
    with col2:
        # 모드 선택
        mode = st.selectbox(
            "출력 모드 선택:",
            ["일반", "HTML"],
            help="일반: 텍스트 형태로 재작성\nHTML: 웹사이트용 HTML 코드로 재작성"
        )
        
        # 글자수 표시
        if original_text:
            char_count = count_characters(original_text)
            word_count = len(original_text.split()) if original_text else 0
            line_count = len(original_text.splitlines()) if original_text else 0
            
            st.markdown(f"""
            <div class="stats-container">
                <h4>📊 원본 글 통계</h4>
                <p><strong>글자수:</strong> {char_count:,}자 (공백/이모지 제외)</p>
                <p><strong>단어수:</strong> {word_count:,}개</p>
                <p><strong>줄수:</strong> {line_count:,}줄</p>
            </div>
            """, unsafe_allow_html=True)
    
    # 재작성 버튼
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 AI 글 재작성 시작", use_container_width=True, disabled=not original_text):
            if not original_text.strip():
                st.warning("재작성할 글을 입력해주세요.")
                return
            
            # 진행률 표시
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("🤖 Gemini AI가 글을 분석하고 있습니다...")
            progress_bar.progress(25)
            time.sleep(1)
            
            status_text.text("✍️ 전문적인 글로 재작성하고 있습니다...")
            progress_bar.progress(50)
            
            # 글 재작성 실행
            result = rewrite_content(original_text, mode)
            
            progress_bar.progress(75)
            status_text.text("📝 최종 검토 및 품질 확인 중...")
            time.sleep(1)
            
            progress_bar.progress(100)
            status_text.text("✅ 재작성 완료!")
            time.sleep(0.5)
            
            # 진행률 표시 제거
            progress_bar.empty()
            status_text.empty()
            
            if result:
                # 결과 저장
                st.session_state.rewrite_result = result
                st.session_state.rewrite_mode = mode
                st.session_state.original_text = original_text
                st.success("🎉 글 재작성이 완료되었습니다!")
            else:
                st.error("글 재작성 중 오류가 발생했습니다. 다시 시도해주세요.")
    
    # 결과 표시
    if 'rewrite_result' in st.session_state and st.session_state.rewrite_result:
        st.markdown("---")
        st.markdown("### 📄 재작성 결과")
        
        result_text = st.session_state.rewrite_result
        result_mode = st.session_state.get('rewrite_mode', '일반')
        
        # 제목과 본문 분리
        if "제목:" in result_text:
            parts = result_text.split("\n\n", 1)
            title_part = parts[0]
            content_part = parts[1] if len(parts) > 1 else ""
            
            # 제목 표시
            if "제목:" in title_part:
                title = title_part.replace("제목:", "").strip()
                st.markdown(f"#### 📌 제목: {title}")
        else:
            content_part = result_text
        
        # 본문 표시
        if result_mode == "HTML":
            # HTML 모드
            st.markdown("#### 🌐 HTML 코드:")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**HTML 소스코드:**")
                st.code(content_part, language="html")
            
            with col2:
                st.markdown("**미리보기:**")
                st.components.v1.html(content_part, height=400, scrolling=True)
                
        else:
            # 일반 모드
            st.markdown("#### 📝 재작성된 글:")
            
            st.markdown(f"""
            <div class="result-container" style="
                background: #ffffff !important;
                color: #333333 !important;
                padding: 1.5rem;
                border-radius: 12px;
                box-shadow: 0 2px 12px rgba(0,0,0,0.1);
                border: 1px solid rgba(32, 178, 170, 0.2);
                line-height: 1.6;
                font-size: 14px;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            ">
                <div style="color: #333333 !important;">
                    {content_part.replace(chr(10), '<br>')}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # 결과 통계
        result_char_count = count_characters(content_part)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            original_text_stored = st.session_state.get('original_text', '')
            original_char_count = count_characters(original_text_stored) if original_text_stored else 0
            char_diff = result_char_count - original_char_count
            
            st.metric(
                "📊 재작성 글자수",
                f"{result_char_count:,}자",
                f"{char_diff:+,}자" if original_char_count > 0 else "신규 작성"
            )
        
        with col2:
            st.metric(
                "🎯 목표 달성률",
                f"{min(100, (result_char_count / 2500) * 100):.1f}%",
                "2500자 기준" if result_char_count >= 2500 else "목표 미달"
            )
        
        with col3:
            original_text_stored = st.session_state.get('original_text', '')
            original_word_count = len(original_text_stored.split()) if original_text_stored else 0
            result_word_count = len(result_text.split())
            
            if original_word_count > 0:
                improvement = ((result_word_count - original_word_count) / original_word_count) * 100
                st.metric(
                    "📈 내용 확장률",
                    f"{improvement:+.1f}%",
                    "단어 기준"
                )
            else:
                st.metric(
                    "📈 내용 확장률",
                    f"{result_word_count}개",
                    "신규 단어"
                )
        
        # 다운로드 버튼
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if result_mode == "HTML":
                st.download_button(
                    "💾 HTML 파일 다운로드",
                    content_part,
                    file_name=f"rewritten_content_{int(time.time())}.html",
                    mime="text/html"
                )
            else:
                st.download_button(
                    "💾 텍스트 파일 다운로드",
                    result_text,
                    file_name=f"rewritten_content_{int(time.time())}.txt",
                    mime="text/plain"
                )
        
        with col2:
            if st.button("🔄 새로운 글 재작성", use_container_width=True):
                if 'rewrite_result' in st.session_state:
                    del st.session_state.rewrite_result
                if 'rewrite_mode' in st.session_state:
                    del st.session_state.rewrite_mode
                if 'original_text' in st.session_state:
                    del st.session_state.original_text
                st.rerun()
        
        with col3:
            if st.button("📋 결과 복사", use_container_width=True):
                # 결과 모드에 따라 복사할 내용 결정
                result_mode = st.session_state.get('rewrite_mode', '일반')
                
                st.info("💡 **복사 방법 안내:**\n- 🔗 버튼 클릭: 자동 복사 (브라우저 지원 시)\n- 📝 텍스트 영역: 전체 선택(Ctrl+A) 후 복사(Ctrl+C)")
                
                if result_mode == "HTML":
                    # HTML 모드: HTML 코드만 추출
                    if "HTML:" in result_text:
                        html_content = result_text.split("HTML:")[1].strip()
                    else:
                        html_content = content_part
                    
                    st.success("📋 HTML 코드가 복사 준비되었습니다!")
                    st.markdown("**복사할 HTML 코드:**")
                    st.code(html_content, language="html")
                    
                    # JavaScript를 사용한 클립보드 복사
                    st.markdown(f"""
                    <div style="margin-top: 10px;">
                        <button onclick="copyToClipboard()" style="
                            background: linear-gradient(135deg, #20B2AA, #48D1CC);
                            color: white;
                            border: none;
                            padding: 8px 16px;
                            border-radius: 5px;
                            cursor: pointer;
                            font-weight: 600;
                        ">🔗 HTML 코드 복사</button>
                    </div>
                    
                    <script>
                    function copyToClipboard() {{
                        const htmlCode = `{html_content.replace('`', '\\`')}`;
                        navigator.clipboard.writeText(htmlCode).then(function() {{
                            alert('HTML 코드가 클립보드에 복사되었습니다!');
                        }}, function(err) {{
                            console.error('복사 실패: ', err);
                            // 대체 방법: 텍스트 선택
                            const textArea = document.createElement('textarea');
                            textArea.value = htmlCode;
                            document.body.appendChild(textArea);
                            textArea.select();
                            document.execCommand('copy');
                            document.body.removeChild(textArea);
                            alert('HTML 코드가 클립보드에 복사되었습니다!');
                        }});
                    }}
                    </script>
                    """, unsafe_allow_html=True)
                    
                    # 수동 복사를 위한 텍스트 영역 (HTML 모드)
                    st.markdown("**🌐 수동 복사 (전체 선택 후 Ctrl+C):**")
                    if "HTML:" in result_text:
                        html_content = result_text.split("HTML:")[1].strip()
                    else:
                        html_content = content_part
                    st.text_area(
                        "HTML 코드 (전체 선택 후 복사)",
                        html_content,
                        height=200,
                        key="html_copy_area"
                    )
                    
                else:
                    # 일반 모드: 전체 텍스트
                    st.success("📋 텍스트가 복사 준비되었습니다!")
                    st.markdown("**복사할 텍스트:**")
                    st.code(result_text, language="text")
                    
                    # JavaScript를 사용한 클립보드 복사
                    clean_text = result_text.replace('`', '\\`').replace('\n', '\\n')
                    st.markdown(f"""
                    <div style="margin-top: 10px;">
                        <button onclick="copyTextToClipboard()" style="
                            background: linear-gradient(135deg, #20B2AA, #48D1CC);
                            color: white;
                            border: none;
                            padding: 8px 16px;
                            border-radius: 5px;
                            cursor: pointer;
                            font-weight: 600;
                        ">📝 텍스트 복사</button>
                    </div>
                    
                    <script>
                    function copyTextToClipboard() {{
                        const textContent = `{clean_text}`;
                        navigator.clipboard.writeText(textContent).then(function() {{
                            alert('텍스트가 클립보드에 복사되었습니다!');
                        }}, function(err) {{
                            console.error('복사 실패: ', err);
                            // 대체 방법: 텍스트 선택
                            const textArea = document.createElement('textarea');
                            textArea.value = textContent;
                            document.body.appendChild(textArea);
                            textArea.select();
                            document.execCommand('copy');
                            document.body.removeChild(textArea);
                            alert('텍스트가 클립보드에 복사되었습니다!');
                        }});
                    }}
                    </script>
                    """, unsafe_allow_html=True)
                    
                    # 수동 복사를 위한 텍스트 영역 (일반 모드)
                    st.markdown("**📝 수동 복사 (전체 선택 후 Ctrl+C):**")
                    st.text_area(
                        "재작성된 텍스트 (전체 선택 후 복사)",
                        result_text,
                        height=200,
                        key="text_copy_area"
                    )

def main():
    """글 재작성 페이지 메인"""
    # 페이지 설정
    st.set_page_config(
        page_title="글 재작성 - " + AppConfig.APP_TITLE,
        page_icon="✍️",
        layout=AppConfig.LAYOUT,
        initial_sidebar_state="expanded"
    )
    
    # 세션 초기화
    initialize_session()
    
    # 인증 확인
    if is_logged_in():
        render_content_rewriter_page()
        
        # 푸터
        st.markdown("---")
        st.markdown(
            f"""
            <div style='text-align: center; color: gray; font-size: 12px;'>
            {AppConfig.COPYRIGHT_TEXT}<br>
            AI 글 재작성 도구 - Google Gemini API 활용<br>
            Professional Content Rewriting Tool v1.0
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