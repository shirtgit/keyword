"""
Authentication module for the marketing tool
로그인/로그아웃 기능 및 세션 관리
"""

import streamlit as st
import time
import os
from config import AuthConfig

def initialize_session():
    """세션 상태 초기화 및 기존 세션 복원 시도"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'login_timestamp' not in st.session_state:
        st.session_state.login_timestamp = None
    
    # 기존 로그인 상태가 있으면 유효성 확인
    if st.session_state.logged_in and st.session_state.login_timestamp:
        # 7일이 지났으면 자동 로그아웃
        current_time = time.time()
        login_time = st.session_state.login_timestamp
        if current_time - login_time > (AuthConfig.SESSION_DURATION_DAYS * 24 * 60 * 60):
            logout_user()
    
    # 임시 파일을 통한 세션 복원 시도
    try_restore_from_temp_file()

def try_restore_from_temp_file():
    """임시 파일에서 세션 복원 시도"""
    try:
        session_file = get_session_file_path()
        if os.path.exists(session_file):
            with open(session_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if len(lines) >= 2:
                    username = lines[0].strip()
                    timestamp = float(lines[1].strip())
                    
                    # 세션이 유효한지 확인
                    current_time = time.time()
                    if current_time - timestamp <= (AuthConfig.SESSION_DURATION_DAYS * 24 * 60 * 60):
                        # 유효한 세션이면 복원
                        if username in AuthConfig.LOGIN_CREDENTIALS:
                            st.session_state.logged_in = True
                            st.session_state.username = username
                            st.session_state.login_timestamp = timestamp
                    else:
                        # 만료된 세션 파일 삭제
                        os.remove(session_file)
    except Exception:
        # 에러 발생 시 조용히 무시
        pass

def get_session_file_path() -> str:
    """세션 파일 경로 반환"""
    import tempfile
    temp_dir = tempfile.gettempdir()
    return os.path.join(temp_dir, 'marketing_tool_session.txt')

def save_session_to_file(username: str):
    """세션 정보를 임시 파일에 저장"""
    try:
        session_file = get_session_file_path()
        with open(session_file, 'w', encoding='utf-8') as f:
            f.write(f"{username}\n")
            f.write(f"{time.time()}\n")
    except Exception:
        # 저장 실패 시 조용히 무시
        pass

def clear_session_file():
    """세션 파일 삭제"""
    try:
        session_file = get_session_file_path()
        if os.path.exists(session_file):
            os.remove(session_file)
    except Exception:
        # 삭제 실패 시 조용히 무시
        pass

def authenticate_user(username: str, password: str) -> bool:
    """사용자 인증 처리"""
    return (username in AuthConfig.LOGIN_CREDENTIALS and 
            AuthConfig.LOGIN_CREDENTIALS[username] == password)

def login_user(username: str):
    """사용자 로그인 처리"""
    st.session_state.logged_in = True
    st.session_state.username = username
    st.session_state.login_timestamp = time.time()
    
    # 세션 정보를 파일에 저장 (새로고침 시 유지용)
    save_session_to_file(username)

def logout_user():
    """사용자 로그아웃 처리"""
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.login_timestamp = None
    
    # 저장된 세션 파일 삭제
    clear_session_file()

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
        /* 컨테이너 최적화 */
        .main .block-container {
            padding-top: 2rem !important;
            padding-bottom: 2rem !important;
            max-width: 450px;
            margin: 0 auto;
        }
        
        /* 로그인 카드 - 시스템 테마 대응 */
        .login-card {
            background: var(--background-color, white);
            border-radius: 16px;
            padding: 2.5rem 2rem;
            box-shadow: 0 8px 32px rgba(32, 178, 170, 0.15);
            border: 1px solid rgba(32, 178, 170, 0.2);
            text-align: center;
            margin-bottom: 1rem;
        }
        
        /* 제목 스타일 - 고정 색상으로 가독성 보장 */
        .login-title {
            color: #20B2AA;
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        
        .login-subtitle {
            color: #666666;
            font-size: 1rem;
            margin-bottom: 1.5rem;
        }
        
        /* 버튼 스타일 - 고정 색상 */
        .stButton > button {
            background: linear-gradient(135deg, #20B2AA, #48D1CC) !important;
            color: white !important;
            border: none !important;
            border-radius: 10px;
            font-weight: 600;
            font-size: 1rem;
            padding: 0.7rem 2rem;
            transition: all 0.2s ease;
            box-shadow: 0 3px 12px rgba(32, 178, 170, 0.3);
        }
        
        .stButton > button:hover {
            background: linear-gradient(135deg, #48D1CC, #40E0D0) !important;
            transform: translateY(-1px);
            box-shadow: 0 4px 16px rgba(32, 178, 170, 0.4);
        }
        
        /* 입력 필드 최적화 */
        .stTextInput > div > div > input {
            border-radius: 8px;
            font-size: 1rem;
            padding: 0.7rem;
            border-color: rgba(32, 178, 170, 0.3);
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #20B2AA;
            box-shadow: 0 0 8px rgba(32, 178, 170, 0.2);
        }
        
        /* 여백 최적화 */
        .element-container {
            margin-bottom: 0.8rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # 로그인 카드
    st.markdown(
        """
        <div class="login-card">
            <h1 class="login-title">🔍 마케팅 도구</h1>
            <p class="login-subtitle">by 쇼쇼 | 현대적이고 심플한 로그인</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # 로그인 폼
    with st.form("login_form"):
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
            "로그인",
            use_container_width=True,
            type="primary"
        )
        
        if login_button:
            if username and password:
                if authenticate_user(username, password):
                    login_user(username)
                    st.success("✅ 로그인 성공!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ 잘못된 로그인 정보입니다.")
            else:
                st.warning("⚠️ 모든 필드를 입력해주세요.")
    
    # 간단한 푸터
    st.markdown(
        """
        <div style='text-align: center; color: var(--text-light); font-size: 0.9rem; margin-top: 2rem;'>
        ⓒ 2025 쇼쇼 | 마케팅 도구
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
        
        # 세션 정보 표시
        if st.session_state.get('login_timestamp'):
            days_left = AuthConfig.SESSION_DURATION_DAYS - int((time.time() - st.session_state.login_timestamp) / (24 * 60 * 60))
            if days_left > 0:
                st.caption(f"🔒 세션 유지: {days_left}일 남음")
        
        if st.button("🚪 로그아웃", use_container_width=True):
            logout_user()
            st.success("✅ 로그아웃되었습니다.")
            time.sleep(1)
            st.rerun()