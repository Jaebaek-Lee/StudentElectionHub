import streamlit as st
import pandas as pd
import json
from datetime import datetime
from utils.auth import hash_email
import re

class DataManager:
    def __init__(self):
        self.initialize_data()
    
    def initialize_data(self):
        """Initialize all data structures in session state"""
        if 'participants' not in st.session_state:
            st.session_state.participants = []
        
        if 'teams' not in st.session_state:
            st.session_state.teams = ["팀 1"]
        
        if 'team_assignments' not in st.session_state:
            st.session_state.team_assignments = {}
        
        if 'votes' not in st.session_state:
            st.session_state.votes = []
        
        if 'vote_counts' not in st.session_state:
            st.session_state.vote_counts = {team: 0 for team in st.session_state.teams}
    
    def add_participants_bulk(self, email_text):
        """Add multiple participants from text input"""
        lines = email_text.strip().split('\n')
        success_count = 0
        error_lines = []
        
        for i, line in enumerate(lines):
            email = line.strip()
            if email:
                if self.is_valid_email(email):
                    if email not in st.session_state.participants:
                        st.session_state.participants.append(email)
                        success_count += 1
                    else:
                        error_lines.append(f"라인 {i+1}: 이미 존재하는 이메일 ({email})")
                else:
                    error_lines.append(f"라인 {i+1}: 잘못된 이메일 형식 ({email})")
        
        return success_count, error_lines
    
    def add_participant(self, email):
        """Add a single participant"""
        if self.is_valid_email(email) and email not in st.session_state.participants:
            st.session_state.participants.append(email)
            return True
        return False
    
    def remove_participant(self, email):
        """Remove a participant"""
        if email in st.session_state.participants:
            st.session_state.participants.remove(email)
            # Also remove from team assignments
            if email in st.session_state.team_assignments:
                del st.session_state.team_assignments[email]
            return True
        return False
    
    def assign_team(self, email, team):
        """Assign a team to a participant"""
        if email in st.session_state.participants and team in st.session_state.teams:
            st.session_state.team_assignments[email] = team
            return True
        return False
    
    def get_user_team(self, email):
        """Get the team assigned to a user"""
        return st.session_state.team_assignments.get(email, None)
    
    def is_email_registered(self, email):
        """Check if email is registered"""
        return email in st.session_state.participants
    
    def has_voted(self, email):
        """Check if user has already voted"""
        email_hash = hash_email(email)
        return any(vote['email_hash'] == email_hash for vote in st.session_state.votes)
    
    def cast_vote(self, email, selected_teams):
        """Cast a vote for selected teams"""
        if self.has_voted(email):
            return False, "이미 투표하셨습니다."
        
        if len(selected_teams) != 2:
            return False, "정확히 2개의 팀을 선택해야 합니다."
        
        user_team = self.get_user_team(email)
        if user_team in selected_teams:
            return False, "본인 팀은 선택할 수 없습니다."
        
        # Record vote
        vote_record = {
            'email_hash': hash_email(email),
            'selected_teams': selected_teams,
            'timestamp': datetime.now().isoformat()
        }
        
        st.session_state.votes.append(vote_record)
        
        # Update vote counts
        for team in selected_teams:
            if team in st.session_state.vote_counts:
                st.session_state.vote_counts[team] += 1
        
        return True, "투표가 성공적으로 완료되었습니다!"
    
    def get_voting_stats(self):
        """Get voting statistics"""
        total_participants = len(st.session_state.participants)
        total_votes = len(st.session_state.votes)
        vote_percentage = (total_votes / total_participants * 100) if total_participants > 0 else 0
        
        return {
            'total_participants': total_participants,
            'total_votes': total_votes,
            'vote_percentage': vote_percentage,
            'remaining_votes': total_participants - total_votes
        }
    
    def get_team_stats(self):
        """Get team statistics"""
        team_stats = []
        for team in st.session_state.teams:
            assigned_count = sum(1 for email, assigned_team in st.session_state.team_assignments.items() if assigned_team == team)
            vote_count = st.session_state.vote_counts.get(team, 0)
            
            team_stats.append({
                'team': team,
                'assigned_members': assigned_count,
                'votes_received': vote_count
            })
        
        return team_stats
    
    def get_unassigned_participants(self):
        """Get participants not assigned to any team"""
        return [email for email in st.session_state.participants 
                if email not in st.session_state.team_assignments]
    
    def update_teams(self, new_teams):
        """Update team list"""
        old_teams = set(st.session_state.teams)
        new_teams_set = set(new_teams)
        
        # Remove assignments for deleted teams
        for email, team in list(st.session_state.team_assignments.items()):
            if team not in new_teams_set:
                del st.session_state.team_assignments[email]
        
        # Update vote counts
        new_vote_counts = {}
        for team in new_teams:
            new_vote_counts[team] = st.session_state.vote_counts.get(team, 0)
        
        st.session_state.teams = new_teams
        st.session_state.vote_counts = new_vote_counts
    
    def export_participants(self):
        """Export participants list as text"""
        return '\n'.join(st.session_state.participants)
    
    def get_results_data(self):
        """Get formatted results data for display"""
        results = []
        for team in st.session_state.teams:
            results.append({
                'team': team,
                'votes': st.session_state.vote_counts.get(team, 0)
            })
        
        # Sort by votes descending
        results.sort(key=lambda x: x['votes'], reverse=True)
        return results
    
    def is_valid_email(self, email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
