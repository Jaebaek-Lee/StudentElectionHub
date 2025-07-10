import streamlit as st
from utils.auth import hash_email

def render_student_voting():
    """Render the student voting interface"""
    # Scroll to top on page load
    st.markdown("""
    <script>
    window.scrollTo(0, 0);
    </script>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="main-header">
        <div class="brand-title">🗳️ 팀 프로젝트 투표</div>
        <div class="brand-subtitle">최고의 팀 2곳을 선택해주세요!</div>
    </div>
    """, unsafe_allow_html=True)
    
    # User info
    user_email = st.session_state.user_email
    user_team = st.session_state.user_team
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 👋 투표 참여")
        
        # Check if user has already voted - show completion page only
        if st.session_state.data_manager.has_voted(user_email):
            # Show only completion message and logout - no other content
            st.markdown("""
            <div class="success-message">
                <h2>🎉 투표가 완료되었습니다!</h2>
                <p style="font-size: 1.2rem; margin: 1rem 0;">
                    투표해주셔서 감사합니다.<br>
                    결과는 모든 발표가 끝난 후 공개됩니다.
                </p>
                <p style="font-size: 1rem; opacity: 0.9;">
                    AI바이브코딩 특강 | 코드트리 X 서경대학교 캠퍼스타운
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Single logout button centered
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("🚪 로그아웃하고 메인으로", type="primary", use_container_width=True, key="already_voted_logout"):
                    st.session_state.is_authenticated = False
                    st.session_state.user_email = None
                    st.session_state.user_role = None
                    st.session_state.user_team = None
                    st.session_state.current_page = 'login'
                    st.rerun()
            return
        
        if not user_team:
            st.warning("팀이 할당되지 않았습니다.")
            
            st.markdown("""
            <div style="background: #FFF3CD; border: 2px solid #FFECB5; 
                       border-radius: 10px; padding: 2rem; text-align: center; margin: 2rem 0;">
                <h3>⚠️ 팀 할당 필요</h3>
                <p style="margin: 1rem 0;">
                    투표에 참여하려면 먼저 팀에 할당되어야 합니다.<br>
                    관리자에게 문의하여 팀을 할당받은 후 다시 로그인해주세요.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Single logout button for unassigned users
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("🚪 로그아웃하고 메인으로", type="primary", use_container_width=True, key="unassigned_logout"):
                    st.session_state.is_authenticated = False
                    st.session_state.user_email = None
                    st.session_state.user_role = None
                    st.session_state.user_team = None
                    st.session_state.current_page = 'login'
                    st.rerun()
            return
        
        st.success(f"**{user_team}** 소속으로 인증되었습니다.")
        st.info("본인 팀은 투표 대상에서 자동으로 제외됩니다.")
        
        st.markdown("---")
        
        # Get available teams (excluding user's team)
        available_teams = [team for team in st.session_state.teams if team != user_team]
        
        if len(available_teams) < 2:
            st.error("투표 가능한 팀이 부족합니다. 관리자에게 문의하세요.")
            
            # Logout button for insufficient teams
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("🚪 로그아웃하고 메인으로", type="primary", use_container_width=True, key="insufficient_teams_logout"):
                    st.session_state.is_authenticated = False
                    st.session_state.user_email = None
                    st.session_state.user_role = None
                    st.session_state.user_team = None
                    st.session_state.current_page = 'login'
                    st.rerun()
            return
        
        # Remove this duplicate section since we moved it above
        
        # Initialize selected teams in session state
        if f'selected_teams_{user_email}' not in st.session_state:
            st.session_state[f'selected_teams_{user_email}'] = []
        
        # Display teams with modern card-based selection
        selected_teams = []
        
        st.markdown("### 🎯 투표할 팀을 선택하세요")
        st.markdown("**2개의 팀을 선택해주세요**")
        
        # Create a grid layout for team cards
        for i, team in enumerate(available_teams):
            is_selected = st.checkbox(
                f"**{team}**", 
                key=f"team_{team}_{user_email}",
                label_visibility="visible"
            )
            if is_selected:
                selected_teams.append(team)
                
            # Add minimal visual spacing for mobile
            if i < len(available_teams) - 1:
                st.markdown('<div style="margin: 0.1rem 0;"></div>', unsafe_allow_html=True)
        
        # Update session state
        st.session_state[f'selected_teams_{user_email}'] = selected_teams
        
        st.markdown("---")
        
        # Show selection status with enhanced visual feedback
        selection_count = len(selected_teams)
        
        st.markdown("---")
        
        if selection_count == 0:
            st.info("💡 **투표할 팀을 선택해주세요**")
        elif selection_count == 1:
            st.warning(f"⚠️ **1개 더 선택해주세요** (현재: {selected_teams[0]})")
        elif selection_count == 2:
            st.success(f"✅ **투표 준비 완료!**")
            st.markdown("**선택된 팀:**")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"✅ **{selected_teams[0]}**")
            with col2:
                st.markdown(f"✅ **{selected_teams[1]}**")
        else:
            st.error("❌ **2개만 선택 가능합니다!** 일부 선택을 해제해주세요.")
        
        # Enhanced submit button with better UX
        vote_button_disabled = selection_count != 2
        
        if selection_count == 2:
            button_text = "🗳️ 투표 제출하기"
            button_help = "선택한 2개 팀에 투표합니다"
        else:
            button_text = f"🗳️ 투표 제출 ({selection_count}/2)"
            button_help = "정확히 2개 팀을 선택해야 투표할 수 있습니다"
        
        if st.button(
            button_text,
            type="primary", 
            use_container_width=True,
            disabled=vote_button_disabled,
            help=button_help,
            key="submit_vote"
        ):
            if selection_count == 2:
                success, message = st.session_state.data_manager.cast_vote(user_email, selected_teams)
                
                if success:
                    # Clear the selection from session state
                    if f'selected_teams_{user_email}' in st.session_state:
                        del st.session_state[f'selected_teams_{user_email}']
                    
                    st.balloons()
                    st.success(message)
                    
                    # Force page refresh to show completion state
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.error("정확히 2개의 팀을 선택해주세요.")
        
        # Show voting instructions only if not voted
        if not st.session_state.data_manager.has_voted(user_email):
            st.markdown("---")
            st.markdown("### 📋 투표 안내")
            st.markdown("""
            - **1인 2표**: 각자 2개의 팀을 선택할 수 있습니다
            - **익명성 보장**: 개인 정보는 저장되지 않습니다
            - **본인 팀 제외**: 본인이 속한 팀은 선택할 수 없습니다
            - **중복 투표 불가**: 한 번 투표하면 수정할 수 없습니다
            - **공정한 평가**: 모든 투표는 동일한 가중치를 가집니다
            """)
            
            # Emergency logout
            st.markdown("---")
            if st.button("🚪 로그아웃"):
                st.session_state.is_authenticated = False
                st.session_state.user_email = None
                st.session_state.user_role = None
                st.session_state.user_team = None
                st.session_state.current_page = 'login'
                st.rerun()
