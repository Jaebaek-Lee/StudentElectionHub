import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def render_results_display():
    """Render the public results display"""
    # Scroll to top on page load
    st.markdown("""
    <script>
    window.scrollTo(0, 0);
    </script>
    """, unsafe_allow_html=True)
    
    # Emergency exit button at the top
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col1:
        if st.button("🔙 메인으로", key="top_exit"):
            st.session_state.show_results = False
            st.session_state.is_authenticated = False
            st.session_state.user_email = None
            st.session_state.user_role = None
            st.session_state.current_page = 'login'
            st.rerun()
    
    with col3:
        if st.session_state.user_role == 'admin':
            if st.button("🏠 관리자", key="top_admin"):
                st.session_state.show_results = False
                st.rerun()
    
    st.markdown("""
    <div class="main-header">
        <div class="brand-title">🏆 투표 결과 발표</div>
        <div class="brand-subtitle">AI바이브코딩 특강 팀 프로젝트 투표 결과</div>
        <div class="special-event">
            <strong>최종 결과</strong> | 모든 투표가 완료되었습니다
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Get results data
    results_data = st.session_state.data_manager.get_results_data()
    stats = st.session_state.data_manager.get_voting_stats()
    
    # Overall statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("총 참여자", stats['total_participants'])
    
    with col2:
        st.metric("총 투표수", stats['total_voted'])
    
    with col3:
        st.metric("투표율", f"{stats['participation_rate']:.1f}%")
    
    with col4:
        total_received_votes = sum(results_data['team_votes'].values()) if results_data else 0
        st.metric("총 득표수", total_received_votes)
    
    st.markdown("---")
    
    # Check if there are any actual votes
    if results_data and total_received_votes > 0:
        sorted_results = results_data['sorted_results']
        
        # Winner announcement
        if len(sorted_results) >= 2:
            st.markdown("## 🎉 우승팀 발표")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #FFD700, #FFA500); 
                           color: white; padding: 2rem; border-radius: 15px; 
                           text-align: center; margin: 1rem 0;">
                    <h2>🥇 1위</h2>
                    <h1>{sorted_results[0][0]}</h1>
                    <h2>{sorted_results[0][1]}표</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #C0C0C0, #A0A0A0); 
                           color: white; padding: 2rem; border-radius: 15px; 
                           text-align: center; margin: 1rem 0;">
                    <h2>🥈 2위</h2>
                    <h1>{sorted_results[1][0]}</h1>
                    <h2>{sorted_results[1][1]}표</h2>
                </div>
                """, unsafe_allow_html=True)
        
        # Detailed results chart
        st.markdown("## 📊 전체 결과")
        
        # Create a simple and reliable bar chart using plotly express
        teams = [r[0] for r in sorted_results]
        votes = [r[1] for r in sorted_results]
        
        # Create DataFrame for plotly express
        chart_df = pd.DataFrame({
            '팀': teams,
            '득표수': votes
        })
        
        # Create bar chart with plotly express (more stable)
        fig = px.bar(
            chart_df,
            x='팀',
            y='득표수',
            title="팀별 최종 득표 결과",
            color='득표수',
            color_continuous_scale=['#33BB66', '#FFD700'],
            text='득표수'
        )
        
        fig.update_layout(
            title_x=0.5,
            font=dict(size=14),
            height=500,
            showlegend=False
        )
        
        fig.update_traces(textposition='outside')
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Results table
        st.markdown("## 📋 상세 순위")
        
        df = pd.DataFrame(results_data)
        df.index = range(1, len(df) + 1)
        df.columns = ['팀명', '득표수']
        
        # Style the dataframe
        styled_df = df.style.apply(lambda x: ['background-color: #FFD700' if x.name == 1 
                                            else 'background-color: #C0C0C0' if x.name == 2 
                                            else 'background-color: #F0F8F5' for _ in x], axis=1)
        
        st.dataframe(styled_df, use_container_width=True)
        
        # Percentage breakdown
        st.markdown("## 📈 득표율 분석")
        
        # Pie chart
        fig_pie = px.pie(
            values=votes,
            names=teams,
            title="팀별 득표율",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig_pie.update_layout(
            title=dict(
                font=dict(size=20),
                x=0.5
            ),
            font=dict(size=14)
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Percentage table
        percentage_data = []
        for result in results_data:
            percentage = (result['votes'] / total_received_votes) * 100
            percentage_data.append({
                '순위': results_data.index(result) + 1,
                '팀명': result['team'],
                '득표수': result['votes'],
                '득표율': f"{percentage:.1f}%"
            })
        
        df_percentage = pd.DataFrame(percentage_data)
        st.dataframe(df_percentage, use_container_width=True)
        
        # Congratulations message with votes
        st.markdown("---")
        st.markdown("""
        <div style="background: linear-gradient(135deg, #33BB66, #28A745); 
                   color: white; padding: 2rem; border-radius: 15px; 
                   text-align: center; margin: 2rem 0;">
            <h2>🎊 축하합니다! 🎊</h2>
            <p style="font-size: 1.2rem; margin: 1rem 0;">
                모든 팀이 훌륭한 프로젝트를 발표해주셨습니다.<br>
                여러분의 열정과 노력에 큰 박수를 보냅니다!
            </p>
            <p style="font-size: 1rem; opacity: 0.9;">
                AI바이브코딩 특강 | 코드트리 X 서경대학교 캠퍼스타운
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    else:
        # Show message when no votes yet
        st.markdown("## 📢 투표 대기 중")
        
        st.info("🗳️ 아직 투표가 진행되지 않았습니다.")
        
        st.markdown("""
        <div style="background: #F0F8F5; border: 2px solid #33BB66; 
                   border-radius: 10px; padding: 2rem; text-align: center; margin: 2rem 0;">
            <h3>💡 투표를 시작하려면</h3>
            <p style="margin: 1rem 0;">
                1. 관리자가 참여자를 등록하고 팀을 할당해야 합니다<br>
                2. 참여자들이 이메일로 로그인하여 투표를 진행합니다<br>
                3. 투표가 완료되면 여기에 결과가 표시됩니다
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show current teams
        if st.session_state.teams:
            st.markdown("### 📋 등록된 팀 목록")
            for i, team in enumerate(st.session_state.teams, 1):
                st.write(f"{i}. **{team}**")
    
    # Navigation controls - always show for anyone who can access results
    st.markdown("---")
    st.markdown("### 🔧 페이지 제어")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔙 메인으로 돌아가기", use_container_width=True):
            st.session_state.show_results = False
            st.session_state.is_authenticated = False
            st.session_state.user_email = None
            st.session_state.user_role = None
            st.session_state.current_page = 'login'
            st.rerun()
    
    with col2:
        if st.button("🔄 결과 새로고침", use_container_width=True):
            st.rerun()
    
    # Admin controls
    if st.session_state.user_role == 'admin':
        with col3:
            if st.button("🏠 관리자 대시보드", use_container_width=True):
                st.session_state.show_results = False
                st.rerun()
    
    # Auto-refresh for live updates
    if st.checkbox("실시간 업데이트 (10초마다)"):
        import time
        time.sleep(10)
        st.rerun()
