"""
Authentication module for the marketing tool
로그인/로그아웃 기능 및 세션 관리
"""

import streamlit as st
import time
from config import AuthConfig

def initialize_session():
    """세션 상태 초기화"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = None

def authenticate_user(username: str, password: str) -> bool:
    """사용자 인증 처리"""
    return (username in AuthConfig.LOGIN_CREDENTIALS and 
            AuthConfig.LOGIN_CREDENTIALS[username] == password)

def login_user(username: str):
    """사용자 로그인 처리"""
    st.session_state.logged_in = True
    st.session_state.username = username

def logout_user():
    """사용자 로그아웃 처리"""
    st.session_state.logged_in = False
    st.session_state.username = None

def is_logged_in() -> bool:
    """로그인 상태 확인"""
    return st.session_state.get('logged_in', False)

def get_current_user() -> str:
    """현재 로그인된 사용자 반환"""
    return st.session_state.get('username', None)

def render_login_page():
    """로그인 페이지 렌더링"""
    st.markdown(
        """
        <style>
        /* Streamlit 기본 여백 적절히 조정 */
        .block-container {
            padding-top: 4rem !important;
            padding-bottom: 2rem !important;
        }
        
        /* 로그인 제목 */
        .login-title {
            text-align: center;
            color: #2c3e50;
            margin-bottom: 2rem;
            margin-top: 1rem;
        }
        
        /* 메인 컨테이너 여백 적절히 조정 */
        .main .block-container {
            padding-top: 4rem !important;
            min-height: 80vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        
        /* 전체 앱 컨테이너 */
        .stApp {
            padding-top: 1rem !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # 로그인 컨테이너
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # 로고 및 제목 (배경 박스 없이)
        st.markdown(
            """
            <div class="login-title">
                <h1 style="margin-top: 0rem; margin-bottom: 0.5rem;">🔍 마케팅 도구</h1>
                <h3 style="color: #7f8c8d; margin-top: 0rem;">by 쇼쇼</h3>
                <hr style="border: 1px solid #ecf0f1; margin-top: 1rem;">
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # 로그인 폼
        with st.form("login_form"):
            st.markdown("### 🔐 로그인")
            
            username = st.text_input(
                "아이디",
                placeholder="아이디를 입력하세요",
                key="login_username"
            )
            
            password = st.text_input(
                "비밀번호",
                type="password",
                placeholder="비밀번호를 입력하세요",
                key="login_password"
            )
            
            login_button = st.form_submit_button(
                "🚀 로그인",
                use_container_width=True,
                type="primary"
            )
            
            if login_button:
                if username and password:
                    if authenticate_user(username, password):
                        login_user(username)
                        st.success("✅ 로그인 성공! 마케팅 도구로 이동합니다...")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ 아이디 또는 비밀번호가 올바르지 않습니다.")
                else:
                    st.warning("⚠️ 아이디와 비밀번호를 모두 입력해주세요.")
        

        
        # 푸터
        st.markdown(
            """
            <div style='text-align: center; color: gray; font-size: 12px; margin-top: 2rem;'>
            ⓒ 2025 쇼쇼. 무단 복제 및 배포 금지. All rights reserved.
            </div>
            """,
            unsafe_allow_html=True
        )

def render_logout_section():
    """로그아웃 섹션 렌더링"""
    col1, col2 = st.columns([3, 1])
    with col2:
        st.markdown("---")
        st.markdown(f"👤 **{get_current_user()}**님 환영합니다!")
        if st.button("🚪 로그아웃", use_container_width=True):
            logout_user()
            st.rerun()