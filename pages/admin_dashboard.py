import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

def render_admin_dashboard():
    """Render the admin dashboard"""
    # Scroll to top on page load
    st.markdown("""
    <script>
    window.scrollTo(0, 0);
    </script>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="main-header">
        <div class="brand-title">👨‍💼 관리자 대시보드</div>
        <div class="brand-subtitle">참여자 관리 및 실시간 투표 현황</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Top navigation
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("👥 참여자 관리", use_container_width=True):
            st.session_state.admin_page = "participants"
    
    with col2:
        if st.button("🏆 팀 관리", use_container_width=True):
            st.session_state.admin_page = "teams"
    
    with col3:
        if st.button("📊 투표 현황", use_container_width=True):
            st.session_state.admin_page = "voting"
    
    with col4:
        if st.button("📈 결과 공개", use_container_width=True):
            st.session_state.data_manager.db.set_show_results(True)
            st.session_state.show_results = True
            st.rerun()
    
    # Initialize admin page state
    if 'admin_page' not in st.session_state:
        st.session_state.admin_page = "participants"
    
    st.markdown("---")
    
    # Render selected page
    if st.session_state.admin_page == "participants":
        render_participant_management()
    elif st.session_state.admin_page == "teams":
        render_team_management()
    elif st.session_state.admin_page == "voting":
        render_voting_status()
    
    # Admin logout
    st.markdown("---")
    if st.button("🚪 관리자 로그아웃"):
        st.session_state.is_authenticated = False
        st.session_state.user_email = None
        st.session_state.user_role = None
        st.session_state.current_page = 'login'
        st.rerun()

def render_participant_management():
    """Render participant management interface"""
    st.markdown("## 👥 참여자 관리")
    
    # Statistics
    stats = st.session_state.data_manager.get_voting_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("총 참여자", stats['total_participants'])
    
    with col2:
        st.metric("투표 완료", stats['total_voted'])
    
    with col3:
        st.metric("투표율", f"{stats['participation_rate']:.1f}%")
    
    with col4:
        st.metric("미투표", stats['total_not_voted'])
    
    st.markdown("---")
    
    # Bulk email registration
    st.markdown("### 📧 이메일 일괄 등록")
    
    with st.expander("이메일 일괄 등록", expanded=True):
        email_text = st.text_area(
            "이메일 목록 (한 줄에 하나씩)",
            placeholder="student1@example.com\nstudent2@example.com\nstudent3@example.com",
            height=150
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📋 일괄 등록", type="primary"):
                if email_text.strip():
                    success_count, error_lines = st.session_state.data_manager.add_participants_bulk(email_text)
                    
                    if success_count > 0:
                        st.success(f"✅ {success_count}명이 성공적으로 등록되었습니다.")
                    
                    if error_lines:
                        st.error("❌ 다음 오류가 발생했습니다:")
                        for error in error_lines:
                            st.write(f"- {error}")
                    
                    if success_count > 0:
                        st.rerun()
                else:
                    st.warning("이메일을 입력해주세요.")
        
        with col2:
            if st.button("📋 전체 복사"):
                participants = st.session_state.data_manager.db.get_participants()
                if participants:
                    export_text = st.session_state.data_manager.export_participants()
                    st.code(export_text, language="text")
                else:
                    st.info("등록된 참여자가 없습니다.")
    
    # Individual participant management
    st.markdown("### 👤 개별 참여자 관리")
    
    # Add single participant
    with st.expander("새 참여자 추가"):
        new_email = st.text_input("이메일 주소")
        if st.button("➕ 추가"):
            if new_email and st.session_state.data_manager.add_participant(new_email):
                st.success(f"✅ {new_email}이 추가되었습니다.")
                st.rerun()
            else:
                st.error("이미 존재하거나 잘못된 이메일입니다.")
    
    # Participant list
    participants = st.session_state.data_manager.db.get_participants()
    if participants:
        st.markdown("### 📋 등록된 참여자 목록")
        
        # Create DataFrame for display
        participant_data = []
        all_teams = st.session_state.data_manager.db.get_teams()
        
        for email, info in participants.items():
            team = info.get('team', "미할당")
            voted = "✅" if st.session_state.data_manager.has_voted(email) else "❌"
            
            participant_data.append({
                "이메일": email,
                "팀": team,
                "투표 완료": voted
            })
        
        df = pd.DataFrame(participant_data)
        
        # Display with edit options
        for idx, row in df.iterrows():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"**{row['이메일']}**")
                st.write(f"팀: {row['팀']} | 투표: {row['투표 완료']}")
            
            with col2:
                # Team assignment
                team_options = ["미할당"] + all_teams
                current_team = row['팀'] if row['팀'] != "미할당" else "미할당"
                
                try:
                    current_index = team_options.index(current_team)
                except ValueError:
                    current_index = 0
                
                new_team = st.selectbox(
                    "팀 변경",
                    team_options,
                    index=current_index,
                    key=f"team_{idx}"
                )
                
                if new_team != current_team:
                    if new_team == "미할당":
                        st.session_state.data_manager.db.assign_team(row['이메일'], None)
                    else:
                        st.session_state.data_manager.db.assign_team(row['이메일'], new_team)
                    st.rerun()
            
            with col3:
                if st.button("🗑️", key=f"delete_{idx}", help="삭제", use_container_width=True):
                    st.session_state.data_manager.remove_participant(row['이메일'])
                    st.rerun()
            
            st.markdown("---")
    
    else:
        st.info("등록된 참여자가 없습니다.")

def render_team_management():
    """Render team management interface"""
    st.markdown("## 🏆 팀 관리")
    
    # Team statistics
    team_stats = st.session_state.data_manager.get_team_stats()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 팀별 현황")
        
        for stat in team_stats:
            st.metric(
                f"{stat['team']}",
                f"멤버: {stat['assigned_members']}명",
                f"득표: {stat['votes_received']}표"
            )
    
    with col2:
        st.markdown("### 🔧 팀 설정")
        
        # Edit team names
        with st.expander("팀명 관리", expanded=True):
            st.markdown("#### 팀 목록")
            
            # Display existing teams with delete option
            teams_to_keep = []
            teams_to_delete = []
            all_teams = st.session_state.data_manager.db.get_teams()
            
            for i, team in enumerate(all_teams):
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    new_name = st.text_input(f"팀 {i+1}", value=team, key=f"team_name_{i}")
                    if new_name.strip():
                        teams_to_keep.append(new_name.strip())
                
                with col2:
                    # Prevent deletion if it's the last team
                    can_delete = len(all_teams) > 1
                    
                    if st.button("🗑️", key=f"delete_team_{i}", help="팀 삭제", disabled=not can_delete):
                        if can_delete:
                            st.session_state.data_manager.db.remove_team(team)
                            st.success(f"'{team}' 팀이 삭제되었습니다.")
                            st.rerun()
                
                with col3:
                    # Show team member count
                    team_stats = st.session_state.data_manager.db.get_team_stats()
                    member_count = team_stats["team_counts"].get(team, 0)
                    st.write(f"멤버: {member_count}명")
                    
                    # Show warning if last team
                    if len(all_teams) == 1:
                        st.caption("(마지막 팀)")
            
            st.markdown("---")
            
            # Add new team section
            col1, col2 = st.columns([3, 1])
            
            # Initialize a counter for clearing input
            if 'team_input_clear_counter' not in st.session_state:
                st.session_state.team_input_clear_counter = 0
            
            with col1:
                new_team_name = st.text_input("새 팀 이름", placeholder="새 팀 이름을 입력하세요", key=f"new_team_input_{st.session_state.team_input_clear_counter}")
            
            with col2:
                if st.button("➕ 팀 추가", use_container_width=True):
                    if new_team_name.strip():
                        if st.session_state.data_manager.db.add_team(new_team_name.strip()):
                            # Clear the input field by incrementing the counter to create a new widget key
                            st.session_state.team_input_clear_counter += 1
                            st.success(f"'{new_team_name.strip()}' 팀이 추가되었습니다.")
                            st.rerun()
                        else:
                            st.error("이미 존재하는 팀 이름입니다.")
                    else:
                        st.error("팀 이름을 입력해주세요.")
            
            st.markdown("---")
            
            # Save changes button
            if st.button("💾 변경사항 저장", type="primary", use_container_width=True):
                # Filter out teams that were deleted
                final_teams = [team for team in teams_to_keep if team not in teams_to_delete]
                
                if len(final_teams) > 0:
                    st.session_state.data_manager.update_teams(final_teams)
                    st.success("팀 목록이 저장되었습니다.")
                    st.rerun()
                else:
                    st.error("최소 1개의 팀은 있어야 합니다.")
    
    # Unassigned participants
    unassigned = st.session_state.data_manager.get_unassigned_participants()
    if unassigned:
        st.markdown("### 🔄 미할당 참여자")
        st.warning(f"{len(unassigned)}명의 참여자가 팀에 할당되지 않았습니다.")
        
        for email in unassigned:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**{email}**")
            
            with col2:
                selected_team = st.selectbox(
                    "팀 할당",
                    ["선택하세요"] + st.session_state.teams,
                    key=f"assign_{email}"
                )
                
                if selected_team != "선택하세요":
                    st.session_state.team_assignments[email] = selected_team
                    st.rerun()

def render_voting_status():
    """Render real-time voting status"""
    st.markdown("## 📊 실시간 투표 현황")
    
    # Auto-refresh every 5 seconds
    if st.button("🔄 새로고침"):
        st.rerun()
    
    # Overall statistics
    stats = st.session_state.data_manager.get_voting_stats()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("총 참여자", stats['total_participants'])
    
    with col2:
        st.metric("투표 완료", stats['total_votes'])
    
    with col3:
        st.metric("투표율", f"{stats['vote_percentage']:.1f}%")
    
    # Progress bar
    progress = stats['total_votes'] / stats['total_participants'] if stats['total_participants'] > 0 else 0
    st.progress(progress)
    
    st.markdown("---")
    
    # Voting results chart
    results_data = st.session_state.data_manager.get_results_data()
    
    if results_data:
        # Create bar chart
        teams = [r['team'] for r in results_data]
        votes = [r['votes'] for r in results_data]
        
        fig = px.bar(
            x=teams,
            y=votes,
            title="팀별 득표 현황",
            labels={'x': '팀', 'y': '득표수'},
            color=votes,
            color_continuous_scale='Viridis'
        )
        
        fig.update_layout(
            showlegend=False,
            xaxis_title="팀",
            yaxis_title="득표수",
            font=dict(size=14)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Results table
        st.markdown("### 📋 상세 결과")
        
        df = pd.DataFrame(results_data)
        df.index = range(1, len(df) + 1)
        df.columns = ['팀명', '득표수']
        
        st.dataframe(df, use_container_width=True)
        
        # Top teams highlight
        if len(results_data) >= 2:
            st.markdown("### 🏆 상위 2팀")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.success(f"🥇 **1위: {results_data[0]['team']}** - {results_data[0]['votes']}표")
            
            with col2:
                st.info(f"🥈 **2위: {results_data[1]['team']}** - {results_data[1]['votes']}표")
    
    else:
        st.info("아직 투표가 진행되지 않았습니다.")
    
    # Real-time updates
    st.markdown("---")
    st.markdown("### ⏰ 실시간 업데이트")
    
    # Add auto-refresh
    if st.checkbox("자동 새로고침 (5초마다)"):
        import time
        time.sleep(5)
        st.rerun()
