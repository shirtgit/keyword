import streamlit as st
from config import AppConfig
from auth import initialize_session, is_logged_in, render_login_page, render_logout_section
from ui import render_rank_checker_tab, render_related_keywords_tab, render_dashboard_metrics, render_footer

def marketing_dashboard():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("네이버 마케팅 분석기")
        st.subheader("by 쇼쇼")
    with col2:
        render_logout_section()
    
    st.markdown("---")
    render_dashboard_metrics()
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["순위 확인", "연관 키워드"])
    with tab1:
        render_rank_checker_tab()
    with tab2:
        render_related_keywords_tab()
    
    render_footer()

def main():
    st.set_page_config(
        page_title=AppConfig.APP_TITLE,
        page_icon=AppConfig.APP_ICON,
        layout=AppConfig.LAYOUT,
        initial_sidebar_state="collapsed"
    )
    
    initialize_session()
    
    if is_logged_in():
        marketing_dashboard()
    else:
        render_login_page()

if __name__ == "__main__":
    main()
