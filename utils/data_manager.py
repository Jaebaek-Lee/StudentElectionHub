import streamlit as st
import pandas as pd
import json
from datetime import datetime
from utils.auth import hash_email
from utils.db_manager import DatabaseManager
import re

class DataManager:
    def __init__(self):
        self.db = DatabaseManager()
    
    def initialize_data(self):
        """Initialize data - handled by database"""
        pass
    
    def add_participants_bulk(self, email_text):
        """Add multiple participants from text input"""
        lines = email_text.strip().split('\n')
        success_count = 0
        error_lines = []
        
        for i, line in enumerate(lines):
            email = line.strip()
            if email:
                if self.is_valid_email(email):
                    if self.db.add_participant(email):
                        success_count += 1
                    else:
                        error_lines.append(f"라인 {i+1}: 이미 존재하는 이메일 ({email})")
                else:
                    error_lines.append(f"라인 {i+1}: 잘못된 이메일 형식 ({email})")
        
        return success_count, error_lines
    
    def add_participant(self, email):
        """Add a single participant"""
        if self.is_valid_email(email):
            return self.db.add_participant(email)
        return False
    
    def remove_participant(self, email):
        """Remove a participant"""
        return self.db.remove_participant(email)
    
    def assign_team(self, email, team):
        """Assign a team to a participant"""
        return self.db.assign_team(email, team)
    
    def get_user_team(self, email):
        """Get the team assigned to a user"""
        return self.db.get_user_team(email)
    
    def is_email_registered(self, email):
        """Check if email is registered"""
        return self.db.is_email_registered(email)
    
    def has_voted(self, email):
        """Check if user has already voted"""
        email_hash = hash_email(email)
        return self.db.has_voted(email_hash)
    
    def cast_vote(self, email, selected_teams):
        """Cast a vote for selected teams"""
        if self.has_voted(email):
            return False, "이미 투표하셨습니다."
        
        if len(selected_teams) != 2:
            return False, "정확히 2개의 팀을 선택해야 합니다."
        
        user_team = self.get_user_team(email)
        if user_team in selected_teams:
            return False, "본인 팀은 선택할 수 없습니다."
        
        # Record vote in database
        email_hash = hash_email(email)
        if self.db.cast_vote(email_hash, selected_teams):
            return True, "투표가 성공적으로 완료되었습니다!"
        else:
            return False, "투표 처리 중 오류가 발생했습니다."
    
    def get_voting_stats(self):
        """Get voting statistics"""
        return self.db.get_voting_stats()
    
    def get_team_stats(self):
        """Get team statistics"""
        stats = self.db.get_team_stats()
        team_stats = []
        
        for team, assigned_count in stats["team_counts"].items():
            # Get vote count for this team from results
            results = self.db.get_results_data()
            vote_count = results["team_votes"].get(team, 0)
            
            team_stats.append({
                'team': team,
                'assigned_members': assigned_count,
                'votes_received': vote_count
            })
        
        return team_stats
    
    def get_unassigned_participants(self):
        """Get participants not assigned to any team"""
        participants = self.db.get_participants()
        return [email for email, info in participants.items() if not info.get('team')]
    
    def update_teams(self, new_teams):
        """Update team list"""
        self.db.update_teams(new_teams)
    
    def export_participants(self):
        """Export participants list as text"""
        participants = self.db.get_participants()
        return '\n'.join(participants.keys())
    
    def get_results_data(self):
        """Get formatted results data for display"""
        return self.db.get_results_data()
    
    def is_valid_email(self, email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
