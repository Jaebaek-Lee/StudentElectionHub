# AI바이브코딩 투표 시스템

## Overview

This is a web-based voting system for AI바이브코딩 (AI Vibe Coding) team project presentations. The application allows students to anonymously vote for their favorite teams (2 votes per student) while providing administrators with real-time monitoring capabilities and result control. The system is built with Streamlit for rapid deployment and ease of use.

## Recent Changes (July 10, 2025)

- **PostgreSQL Database Integration**: Complete migration from temporary file storage to persistent PostgreSQL database
  - Resolved session isolation issues that prevented data sharing between admin and students
  - Implemented Neon PostgreSQL for production deployment on Streamlit Community Cloud
  - All data (participants, teams, votes) now permanently stored and synchronized across sessions
  - Database schema includes proper relationships and constraints for data integrity
- **Dynamic Team Management**: Implemented proper team deletion with assignment cleanup and prevention of last team deletion
- **Mobile Optimization**: Added comprehensive mobile-first CSS for 100% mobile user base (excluding admin)
- **Team Input Clearing**: Fixed team addition input field to auto-clear after successful team creation using dynamic widget keys
- **UI Simplification**: Removed unnecessary edit buttons from participant management interface
- **Post-Vote UI**: Enhanced voting completion experience with complete UI transformation hiding all voting elements
- **Ultra UX/UI Enhancement**: Comprehensive mobile-first design overhaul with enhanced visual feedback, card-based layouts, and professional styling
- **Enhanced Voting Interface**: Improved team selection with better visual hierarchy, status indicators, and touch-friendly mobile optimization
- **Authentication Redesign**: Modernized login interface with button-based navigation and enhanced mobile responsiveness
- **Ultra-Compact Mobile Layout**: Dramatically reduced vertical spacing between all interactive elements for mobile devices
  - Button margins reduced from 0.25rem to 0.1rem
  - Checkbox padding and margins minimized (0.5rem padding, 0.2rem margin)
  - Element containers optimized (0.3rem margin)
  - Visual spacing between voting options reduced to 0.1rem
  - Page-level padding reduced for small screens (0.5rem top/bottom padding)
  - Heading margins compressed for mobile (h1: 0.8rem, h2: 0.6rem, h3: 0.5rem)
- **Security Enhancement**: Removed exposed admin credentials from UI and implemented secure environment variable authentication
  - Admin credentials no longer displayed in interface
  - Required ADMIN_EMAIL and ADMIN_PASSWORD environment variables for secure access
  - Enhanced authentication validation with proper error handling
- **Production Deployment Ready**: Configured for external PostgreSQL database deployment on Streamlit Community Cloud
  - Environment variables configured for DATABASE_URL, ADMIN_EMAIL, ADMIN_PASSWORD
  - Database connection established with Neon PostgreSQL service
  - System ready for 5-hour voting event deployment

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit - chosen for rapid prototyping and deployment without complex setup
- **UI Components**: Custom CSS with gradient branding, responsive design optimized for mobile devices
- **State Management**: Streamlit session state for user authentication, voting data, and application state
- **Visualization**: Plotly for interactive charts and real-time voting results display
- **Styling**: Custom CSS with Korean branding for AI바이브코딩 special event

### Backend Architecture
- **Application Structure**: Modular design with separate page components for different user roles
- **Data Storage**: In-memory storage using Streamlit session state (no persistent database required)
- **Authentication**: Email-based authentication for students with pre-registration; admin login with credentials
- **Session Management**: Streamlit's built-in session handling with role-based access control
- **Anonymous Voting**: SHA-256 email hashing to ensure voter anonymity while preventing duplicate votes

## Key Components

### 1. Authentication System (`utils/auth.py`)
- **Student Authentication**: 
  - Email-based login with pre-registered participant list
  - Immediate access after email verification
  - Anonymous voting through email hashing
- **Admin Authentication**: 
  - Username/password system with environment variable configuration
  - Environment-based credentials (no default values)
- **Team Assignment**: Maps users to teams to automatically exclude own team from voting options

### 2. Data Management (`utils/data_manager.py`)
- **In-memory Storage**: All data persisted in Streamlit session state during session
- **Participant Management**: 
  - Bulk email import with line-by-line parsing
  - Email validation and duplicate prevention
  - Team assignment functionality with automatic cleanup on team deletion
- **Vote Tracking**: 
  - Real-time vote counting with duplicate prevention
  - Anonymous vote storage using hashed email identifiers
- **Team Management**: Dynamic team creation starting with 1 team, expandable with add/delete functionality
  - Minimum 1 team enforcement (cannot delete last remaining team)
  - Automatic cleanup of team assignments when teams are deleted
  - Input field auto-clearing after team addition

### 3. Page Components
- **Authentication Page** (`pages/auth_page.py`): Tabbed interface for student and admin login
- **Student Voting** (`pages/student_voting.py`): 
  - Clean voting interface with team selection
  - Automatic exclusion of user's own team
  - Two-vote requirement with validation
  - Mobile-optimized design
- **Admin Dashboard** (`pages/admin_dashboard.py`): 
  - Multi-tab interface for participant, team, and voting management
  - Real-time monitoring capabilities
  - Results control and public display toggle
- **Results Display** (`pages/results_display.py`): Public results visualization with interactive charts

### 4. Main Application (`app.py`)
- **Route Management**: Handles navigation between different user interfaces
- **State Control**: Manages authentication states and user roles
- **Custom Styling**: Implements Korean branding and responsive design
- **Session Initialization**: Sets up data structures and user sessions

## Data Flow

### Student Voting Flow
1. Student enters email on authentication page
2. System validates email against pre-registered participant list
3. User is assigned to team and authenticated
4. Voting interface displays all teams except user's own team
5. Student selects exactly 2 teams and submits vote
6. Vote is recorded with hashed email identifier
7. System prevents duplicate voting attempts

### Admin Management Flow
1. Admin logs in with credentials
2. Admin can manage participants through bulk email import
3. Admin assigns participants to teams
4. Admin monitors real-time voting statistics
5. Admin controls public results display
6. Admin can view detailed analytics and export data

## External Dependencies

### Python Libraries
- **streamlit**: Core web framework for rapid application development
- **pandas**: Data manipulation and analysis for participant and voting data
- **plotly**: Interactive charting and visualization for results display
- **hashlib**: Built-in library for anonymous email hashing
- **re**: Built-in library for email validation
- **os**: Built-in library for environment variable access
- **datetime**: Built-in library for timestamp management
- **json**: Built-in library for data serialization (if needed)

### Environment Variables
- `ADMIN_EMAIL`: Admin login email (required environment variable)
- `ADMIN_PASSWORD`: Admin login password (required environment variable)

## Deployment Strategy

### Streamlit Community Cloud Deployment
- **Platform**: Streamlit Community Cloud for free hosting
- **Repository**: GitHub repository with public access
- **Configuration**: `.streamlit/config.toml` for Streamlit-specific settings
- **Dependencies**: `requirements.txt` for Python package management
- **Environment**: Environment variables configured through Streamlit Cloud interface

### Local Development
- **Setup**: Simple `streamlit run app.py` command
- **Dependencies**: Install via `pip install -r requirements.txt`
- **Configuration**: Local environment variables or default values

### Key Architectural Decisions

1. **In-Memory Storage**: Chosen over persistent database for simplicity and quick deployment
   - **Pros**: No database setup required, faster development, suitable for single-session events
   - **Cons**: Data loss on application restart, not suitable for long-term storage

2. **Streamlit Framework**: Selected for rapid prototyping and deployment
   - **Pros**: Quick development, built-in authentication, easy deployment
   - **Cons**: Limited scalability, session-based limitations

3. **Anonymous Voting**: Email hashing ensures voter privacy while preventing duplicates
   - **Pros**: Maintains anonymity, prevents duplicate votes, simple implementation
   - **Cons**: Cannot track individual vote changes, relies on session state

4. **Role-Based Access**: Separate interfaces for students and administrators
   - **Pros**: Clear separation of concerns, appropriate access levels
   - **Cons**: Single admin account limitation, no advanced user management

5. **Mobile-First Design**: Comprehensive mobile optimization for 100% mobile user base (students)
   - **Pros**: Touch-friendly interfaces, larger buttons and inputs, optimized typography for mobile screens
   - **Implementation**: Responsive breakpoints at 768px and 480px with enhanced mobile styling
   - **Features**: Larger checkboxes, improved spacing, container width optimization