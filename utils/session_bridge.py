import streamlit as st
import json
import hashlib
from datetime import datetime

class SessionBridge:
    """Bridge session data across browser tabs using URL parameters and localStorage"""
    
    def __init__(self):
        self.initialize_shared_state()
    
    def initialize_shared_state(self):
        """Initialize shared state with localStorage backup"""
        # Global data key for this voting session
        if 'global_session_id' not in st.session_state:
            st.session_state.global_session_id = hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8]
        
        # Initialize core data structures if not present
        if 'shared_participants' not in st.session_state:
            st.session_state.shared_participants = []
        
        if 'shared_teams' not in st.session_state:
            st.session_state.shared_teams = ["팀 1"]
        
        if 'shared_team_assignments' not in st.session_state:
            st.session_state.shared_team_assignments = {}
        
        if 'shared_votes' not in st.session_state:
            st.session_state.shared_votes = []
        
        if 'shared_vote_counts' not in st.session_state:
            st.session_state.shared_vote_counts = {team: 0 for team in st.session_state.shared_teams}
        
        if 'shared_show_results' not in st.session_state:
            st.session_state.shared_show_results = False
    
    def sync_data_to_url(self):
        """Sync current data to URL parameters for sharing"""
        try:
            # Create compact data object
            data = {
                'p': list(st.session_state.shared_participants),  # participants
                't': st.session_state.shared_teams,  # teams
                'a': st.session_state.shared_team_assignments,  # assignments
                'v': len(st.session_state.shared_votes),  # vote count only
                'r': st.session_state.shared_show_results  # show results
            }
            
            # Encode to base64 for URL
            import base64
            json_str = json.dumps(data, ensure_ascii=False)
            encoded_data = base64.b64encode(json_str.encode('utf-8')).decode('ascii')
            
            # Store in session for URL generation
            st.session_state.encoded_data = encoded_data
            
        except Exception as e:
            # Fallback: use session state only
            pass
    
    def load_data_from_url(self):
        """Load data from URL parameters if available"""
        try:
            # Check if data parameter exists in URL
            query_params = st.experimental_get_query_params()
            
            if 'data' in query_params:
                import base64
                encoded_data = query_params['data'][0]
                json_str = base64.b64decode(encoded_data.encode('ascii')).decode('utf-8')
                data = json.loads(json_str)
                
                # Load data into session state
                st.session_state.shared_participants = data.get('p', [])
                st.session_state.shared_teams = data.get('t', ["팀 1"])
                st.session_state.shared_team_assignments = data.get('a', {})
                st.session_state.shared_show_results = data.get('r', False)
                
                # Rebuild vote counts
                st.session_state.shared_vote_counts = {team: 0 for team in st.session_state.shared_teams}
                
                return True
                
        except Exception as e:
            # Fallback to default initialization
            pass
        
        return False
    
    def get_shareable_url(self):
        """Generate shareable URL with current data"""
        try:
            self.sync_data_to_url()
            if hasattr(st.session_state, 'encoded_data'):
                base_url = st.experimental_get_query_params().get('base_url', [''])[0]
                if not base_url:
                    # Use current URL as base
                    base_url = "YOUR_DEPLOYED_URL"  # Replace with actual deployed URL
                
                return f"{base_url}?data={st.session_state.encoded_data}"
        except:
            pass
        
        return "현재 URL을 복사하여 공유하세요"
    
    def display_admin_instructions(self):
        """Display instructions for admin to share data"""
        st.markdown("### 📢 학생 투표 링크 공유")
        
        # Try to generate shareable URL
        shareable_url = self.get_shareable_url()
        
        if shareable_url != "현재 URL을 복사하여 공유하세요":
            st.code(shareable_url, language=None)
            st.info("위 링크를 학생들에게 공유하세요. 참여자 데이터가 포함되어 있습니다.")
        else:
            st.warning("""
            **학생들에게 안내할 내용:**
            1. 현재 브라우저 URL을 복사하여 학생들에게 공유
            2. 학생들은 새 탭이 아닌 새 브라우저 창으로 접속
            3. 접속 후 등록된 이메일로 로그인
            """)
        
        # Alternative: Manual data sharing
        st.markdown("### 🔄 대안: 수동 데이터 공유")
        if st.button("참여자 목록 복사용 텍스트 생성"):
            participants_text = "\n".join(st.session_state.shared_participants)
            st.text_area("참여자 목록 (복사해서 학생용 창에 붙여넣기)", 
                        participants_text, height=200)
    
    def display_data_import(self):
        """Display data import interface for students/other sessions"""
        st.markdown("### 📥 참여자 데이터 가져오기")
        st.info("관리자로부터 받은 참여자 목록을 붙여넣으세요.")
        
        imported_data = st.text_area("참여자 이메일 목록", height=200, 
                                   placeholder="email1@example.com\nemail2@example.com")
        
        if st.button("데이터 가져오기"):
            if imported_data.strip():
                lines = imported_data.strip().split('\n')
                imported_participants = [line.strip() for line in lines if line.strip()]
                
                # Update shared participants
                st.session_state.shared_participants = imported_participants
                
                # Reset assignments and votes for imported data
                st.session_state.shared_team_assignments = {}
                st.session_state.shared_votes = []
                st.session_state.shared_vote_counts = {team: 0 for team in st.session_state.shared_teams}
                
                st.success(f"{len(imported_participants)}명의 참여자가 가져와졌습니다.")
                st.rerun()
    
    def check_and_load_url_data(self):
        """Check and load data from URL on app start"""
        if not hasattr(st.session_state, 'data_loaded_from_url'):
            if self.load_data_from_url():
                st.session_state.data_loaded_from_url = True
                st.success("공유된 데이터를 성공적으로 로드했습니다!")
                return True
            else:
                st.session_state.data_loaded_from_url = False
        
        return False