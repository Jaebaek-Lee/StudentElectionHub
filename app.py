import streamlit as st
import os
from utils.data_manager import DataManager
from utils.auth import verify_admin, is_valid_email, get_user_team
from pages.admin_dashboard import render_admin_dashboard
from pages.student_voting import render_student_voting
from pages.results_display import render_results_display
from pages.auth_page import render_auth_page

# Page configuration
st.set_page_config(
    page_title="AI바이브코딩 투표 시스템",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #33BB66, #28A745);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .brand-title {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .brand-subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
        margin-bottom: 1rem;
    }
    
    .special-event {
        background: rgba(255, 255, 255, 0.2);
        padding: 0.5rem 1rem;
        border-radius: 10px;
        font-size: 1rem;
        margin-top: 1rem;
    }
    
    .success-message {
        background: linear-gradient(135deg, #33BB66, #28A745);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin: 2rem 0;
    }
    
    .success-message h2 {
        margin-bottom: 1rem;
        font-size: 2rem;
    }
    
    .success-message p {
        margin: 0.5rem 0;
        font-size: 1.1rem;
    }
    
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s ease;
        background: linear-gradient(135deg, #33BB66, #28A745) !important;
        color: white !important;
        border-color: transparent !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        background: linear-gradient(135deg, #28A745, #1E7E34) !important;
        border-color: transparent !important;
    }
    
    .stButton > button:focus {
        background: linear-gradient(135deg, #33BB66, #28A745) !important;
        color: white !important;
        border-color: transparent !important;
        box-shadow: 0 0 0 2px rgba(51, 187, 102, 0.3) !important;
    }
    
    .stButton > button:active {
        background: linear-gradient(135deg, #28A745, #1E7E34) !important;
        color: white !important;
        border-color: transparent !important;
    }
    
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #33BB66;
        margin: 0.5rem 0;
    }
    
    .team-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border: 1px solid #e9ecef;
    }
    
    .team-card:hover {
        background: #e9ecef;
        transition: all 0.3s ease;
    }
    
    /* Enhanced voting interface */
    .stCheckbox {
        background: #ffffff;
        border: 2px solid #e9ecef;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .stCheckbox:hover {
        border-color: #33BB66;
        box-shadow: 0 4px 12px rgba(51, 187, 102, 0.15);
        transform: translateY(-2px);
    }
    
    .stCheckbox > label {
        font-size: 1.2rem;
        font-weight: 600;
        color: #2c3e50;
        padding: 0.5rem 0;
    }
    
    .stCheckbox input:checked + div {
        background: linear-gradient(135deg, #33BB66, #28A745);
        color: white;
        border-radius: 10px;
        padding: 0.25rem;
    }
    
    .info-box {
        background: #e3f2fd;
        border: 1px solid #2196f3;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    /* Admin button styling */
    button[data-testid="admin_btn"] {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
        border: none !important;
    }
    
    button[data-testid="admin_btn"]:hover {
        background: linear-gradient(135deg, #764ba2, #5a4a92) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
    }
    
    /* Student button styling */
    button[data-testid="student_btn"] {
        background: linear-gradient(135deg, #33BB66, #28A745) !important;
        color: white !important;
        border: none !important;
    }
    
    button[data-testid="student_btn"]:hover {
        background: linear-gradient(135deg, #28A745, #1E7E34) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
    }
    
    /* Mobile-first optimizations */
    @media (max-width: 768px) {
        .main-header {
            margin-bottom: 1rem;
        }
        
        .brand-title {
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }
        
        .brand-subtitle {
            font-size: 1rem;
            margin-bottom: 0.5rem;
        }
        
        .special-event {
            font-size: 0.9rem;
            padding: 0.5rem;
            margin-top: 0.5rem;
        }
        
        .success-message {
            padding: 1.5rem;
            margin: 1rem 0;
        }
        
        /* Reduce spacing between sections */
        .stMarkdown {
            margin-bottom: 0.5rem;
        }
        
        hr {
            margin: 1rem 0;
        }
        
        .footer {
            margin-top: 1rem;
        }
        
        .login-container {
            padding: 1rem;
            margin: 1rem 0;
        }
        
        .stForm {
            margin-bottom: 1rem;
        }
        
        .stTextInput {
            margin-bottom: 0.5rem;
        }
        
        .stButton {
            margin-bottom: 0.1rem;
        }
        
        .stButton > button {
            padding: 0.6rem 1rem;
            font-size: 1rem;
            margin: 0.1rem 0;
            border-radius: 10px;
            font-weight: 600;
            min-height: auto;
        }
        
        .stTextInput input {
            font-size: 1.1rem;
            padding: 1rem;
            border-radius: 12px;
        }
        
        .stCheckbox {
            padding: 0.5rem;
            margin: 0.2rem 0;
            border-radius: 10px;
        }
        
        .stCheckbox > label {
            font-size: 1.1rem;
            font-weight: 600;
        }
        
        .stSelectbox select {
            font-size: 1.1rem;
            padding: 1rem;
            border-radius: 12px;
        }
        
        .team-card {
            padding: 2rem;
            margin: 1.5rem 0;
            border-radius: 20px;
        }
        
        .metric-card {
            padding: 2rem;
            margin: 1.5rem 0;
            border-radius: 15px;
        }
        
        .main-header {
            padding: 2rem;
            margin-bottom: 1.5rem;
            border-radius: 20px;
        }
        
        /* Better spacing for mobile */
        .main > div {
            padding: 1.5rem;
        }
        
        /* Improved column layout for mobile */
        .row-widget {
            flex-direction: column;
        }
        
        .row-widget > div {
            margin: 1rem 0;
        }
        
        /* Enhanced mobile voting interface */
        .element-container {
            margin: 0.3rem 0;
        }
        
        /* Better touch targets */
        .stButton > button:active {
            transform: scale(0.98);
        }
        
        .stCheckbox:active {
            transform: scale(0.98);
        }
    }
    
    /* Extra small screens */
    @media (max-width: 480px) {
        .brand-title {
            font-size: 1.8rem;
            line-height: 1.3;
        }
        
        .brand-subtitle {
            font-size: 1rem;
        }
        
        .success-message {
            padding: 2.5rem 1.5rem;
            border-radius: 25px;
        }
        
        .success-message h2 {
            font-size: 1.6rem;
            margin-bottom: 1.5rem;
        }
        
        .success-message p {
            font-size: 1rem;
            line-height: 1.7;
        }
        
        .stButton > button {
            padding: 0.6rem 1.2rem;
            font-size: 1.1rem;
            border-radius: 10px;
            margin: 0.1rem 0;
            min-height: auto;
        }
        
        .stTextInput input {
            font-size: 1.2rem;
            padding: 1.25rem;
            border-radius: 15px;
        }
        
        .stCheckbox {
            padding: 0.5rem;
            margin: 0.2rem 0;
            border-radius: 10px;
        }
        
        .stCheckbox > label {
            font-size: 1.2rem;
            font-weight: 600;
            line-height: 1.2;
        }
        
        .team-card {
            padding: 2.5rem;
            border-radius: 25px;
        }
        
        .metric-card {
            padding: 2.5rem;
            border-radius: 20px;
        }
        
        .main-header {
            padding: 2rem 1.5rem;
            border-radius: 25px;
        }
        
        /* Ultra-mobile optimization */
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
            padding-top: 0.5rem;
            padding-bottom: 0.5rem;
        }
        
        /* Better visual hierarchy on small screens */
        h1 {
            font-size: 1.8rem;
            margin-bottom: 0.8rem;
        }
        
        h2 {
            font-size: 1.5rem;
            margin-bottom: 0.6rem;
        }
        
        h3 {
            font-size: 1.3rem;
            margin-bottom: 0.5rem;
        }
    }
    
    .warning-box {
        background: #fff3e0;
        border: 1px solid #ff9800;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .error-box {
        background: #ffebee;
        border: 1px solid #f44336;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .success-box {
        background: #e8f5e8;
        border: 1px solid #4caf50;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(135deg, #33BB66, #28A745);
    }
    
    .stSelectbox > div > div {
        border-radius: 10px;
    }
    
    .stTextInput > div > div {
        border-radius: 10px;
    }
    
    .stTextArea > div > div {
        border-radius: 10px;
    }
    
    .stCheckbox > label {
        font-weight: bold;
        font-size: 1.1rem;
    }
    
    .stRadio > label {
        font-weight: bold;
        font-size: 1.1rem;
    }
    
    .stMetric {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #33BB66;
    }
    
    .stExpander {
        border: 1px solid #e9ecef;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    .stExpander > div {
        border-radius: 10px;
    }
    
    .stTabs > div > div {
        border-radius: 10px 10px 0 0;
    }
    
    .stAlert {
        border-radius: 10px;
    }
    
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    h1, h2, h3 {
        color: #2c3e50;
    }
    
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
    }
    
    .stPlotlyChart {
        border-radius: 10px;
        overflow: hidden;
    }
    
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        background: white;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .admin-login {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
    }
    
    .student-login {
        background: linear-gradient(135deg, #33BB66, #28A745);
        color: white;
    }
    
    .footer {
        text-align: center;
        padding: 2rem;
        color: #6c757d;
        border-top: 1px solid #e9ecef;
        margin-top: 3rem;
    }
</style>
""", unsafe_allow_html=True)

def initialize_app():
    """Initialize the application and session state"""
    # Initialize data manager
    if 'data_manager' not in st.session_state:
        st.session_state.data_manager = DataManager()
    
    # Initialize authentication state
    if 'is_authenticated' not in st.session_state:
        st.session_state.is_authenticated = False
    
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None
    
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    
    if 'user_team' not in st.session_state:
        st.session_state.user_team = None
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'login'
    
    if 'show_results' not in st.session_state:
        st.session_state.show_results = False

def main():
    """Main application entry point"""
    initialize_app()
    
    # Add scroll to top functionality
    st.markdown("""
    <script>
    window.scrollTo(0, 0);
    </script>
    """, unsafe_allow_html=True)
    
    # Check if results should be displayed
    if st.session_state.show_results:
        render_results_display()
        return
    
    # Check authentication status
    if not st.session_state.is_authenticated:
        render_auth_page()
        return
    
    # Route to appropriate page based on user role
    if st.session_state.user_role == 'admin':
        render_admin_dashboard()
    elif st.session_state.user_role == 'student':
        render_student_voting()
    else:
        st.error("인증 오류가 발생했습니다. 다시 로그인해주세요.")
        st.session_state.is_authenticated = False
        st.session_state.user_email = None
        st.session_state.user_role = None
        st.session_state.user_team = None
        st.rerun()

if __name__ == "__main__":
    main()
