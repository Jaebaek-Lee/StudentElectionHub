import streamlit as st
from utils.auth import verify_admin, is_valid_email, get_user_team

def render_auth_page():
    """Render the authentication page"""
    # Scroll to top on page load
    st.markdown("""
    <script>
    window.scrollTo(0, 0);
    </script>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="main-header">
        <div class="brand-title">🗳️ AI바이브코딩 투표 시스템</div>
        <div class="brand-subtitle">팀 프로젝트 발표 투표에 참여하세요</div>
        <div class="special-event">
            <strong>AI바이브코딩 특강</strong> | 코드트리 X 서경대학교 캠퍼스타운
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Create enhanced tab layout with better mobile design
    st.markdown("---")
    
    # Initialize auth mode
    if 'auth_mode' not in st.session_state:
        st.session_state.auth_mode = "student"
    
    # Use columns for better mobile layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("👨‍🎓 학생 로그인", use_container_width=True, key="student_btn"):
            st.session_state.auth_mode = "student"
            st.rerun()
    
    with col2:
        if st.button("👨‍💼 관리자 로그인", use_container_width=True, key="admin_btn"):
            st.session_state.auth_mode = "admin"
            st.rerun()
    
    st.markdown('<hr style="margin: 0.5rem 0;">', unsafe_allow_html=True)
    
    # Render appropriate login form based on selection
    if st.session_state.auth_mode == "student":
        render_student_login()
    else:
        render_admin_login()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div class="footer">
        <p>🏫 <strong>AI바이브코딩 특강</strong></p>
        <p>코드트리 X 서경대학교 캠퍼스타운</p>
        <p>팀 프로젝트 발표 투표 시스템</p>
    </div>
    """, unsafe_allow_html=True)

def render_student_login():
    """Render student login interface"""
    st.markdown("### 👨‍🎓 학생 투표 참여")
    
    st.markdown("""
    <div class="login-container student-login">
        <h3 style="text-align: center; margin-bottom: 1rem; color: white;">학생 로그인</h3>
        <p style="text-align: center; opacity: 0.9; color: white;">
            등록된 이메일 주소로 로그인하세요
        </p>
    </div>
    """, unsafe_allow_html=True)
        
    # Student email input
    with st.form("student_login_form"):
        email = st.text_input(
            "이메일 주소",
            placeholder="student@example.com",
            help="관리자가 사전에 등록한 이메일 주소를 입력하세요"
        )
        
        submit_button = st.form_submit_button("🗳️ 투표 참여하기", use_container_width=True)
            
        if submit_button:
            if not email:
                st.error("이메일을 입력해주세요.")
            elif not is_valid_email(email):
                st.error("올바른 이메일 형식을 입력해주세요.")
            elif not st.session_state.data_manager.is_email_registered(email):
                st.error("등록되지 않은 이메일입니다. 관리자에게 문의하세요.")
            elif st.session_state.data_manager.has_voted(email):
                st.warning("이미 투표를 완료하셨습니다.")
            else:
                # Successful login
                user_team = get_user_team(email, st.session_state.data_manager)
                
                st.session_state.is_authenticated = True
                st.session_state.user_email = email
                st.session_state.user_role = 'student'
                st.session_state.user_team = user_team
                st.session_state.current_page = 'voting'
                
                st.success(f"✅ 로그인 성공! {user_team if user_team else '미할당'} 팀으로 인증되었습니다.")
                st.rerun()
        
    # Instructions
    st.markdown("---")
    st.markdown("### 📋 투표 안내")
    st.markdown("""
    - 사전에 등록된 이메일 주소로만 투표가 가능합니다
    - 1인당 2개 팀을 선택할 수 있습니다
    - 본인이 속한 팀은 투표 대상에서 제외됩니다
    - 투표는 익명으로 진행되며, 한 번만 가능합니다
    - 투표 완료 후 결과는 발표 시간에 공개됩니다
    """)

def render_admin_login():
    """Render admin login interface"""
    st.markdown("### 👨‍💼 관리자 로그인")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="login-container admin-login">
            <h3 style="text-align: center; margin-bottom: 1rem;">관리자 로그인</h3>
            <p style="text-align: center; opacity: 0.9;">
                관리자 계정으로 로그인하세요
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Admin login form
        with st.form("admin_login_form"):
            admin_email = st.text_input(
                "관리자 이메일",
                placeholder="admin@example.com"
            )
            
            admin_password = st.text_input(
                "비밀번호",
                type="password",
                placeholder="비밀번호를 입력하세요"
            )
            
            admin_submit = st.form_submit_button("🔐 관리자 로그인", use_container_width=True)
            
            if admin_submit:
                if not admin_email or not admin_password:
                    st.error("이메일과 비밀번호를 모두 입력해주세요.")
                elif not is_valid_email(admin_email):
                    st.error("올바른 이메일 형식을 입력해주세요.")
                elif not verify_admin(admin_email, admin_password):
                    st.error("관리자 인증에 실패했습니다. 이메일과 비밀번호를 확인해주세요.")
                else:
                    # Successful admin login
                    st.session_state.is_authenticated = True
                    st.session_state.user_email = admin_email
                    st.session_state.user_role = 'admin'
                    st.session_state.user_team = None
                    st.session_state.current_page = 'admin'
                    
                    st.success("✅ 관리자 로그인 성공!")
                    st.rerun()
        
        # Admin instructions
        st.markdown("---")
        st.markdown("### 🔧 관리자 기능")
        st.markdown("""
        - 참여자 이메일 일괄 등록 및 관리
        - 팀 생성 및 참여자 팀 할당
        - 실시간 투표 현황 모니터링
        - 투표 결과 확인 및 공개
        - 투표 통계 및 분석 데이터 조회
        """)
        
        # Admin setup info
        st.markdown("---")
        st.info("""
        **관리자 계정 설정**  
        환경변수 설정이 필요합니다:
        - ADMIN_EMAIL: 관리자 이메일 주소
        - ADMIN_PASSWORD: 관리자 비밀번호
        """)

def render_quick_access():
    """Render quick access buttons"""
    st.markdown("### 🚀 빠른 접속")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 투표 결과 보기", use_container_width=True):
            st.session_state.show_results = True
            st.rerun()
    
    with col2:
        if st.button("🔄 페이지 새로고침", use_container_width=True):
            st.rerun()
