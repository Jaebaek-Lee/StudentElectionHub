import json
import os
import threading
from datetime import datetime

class FileStorage:
    """File-based storage for sharing data across sessions"""
    
    def __init__(self, file_path="voting_data.json"):
        self.file_path = file_path
        self.lock = threading.Lock()
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Ensure the storage file exists with default structure"""
        if not os.path.exists(self.file_path):
            default_data = {
                "participants": {},
                "teams": ["팀 1"],
                "votes": {},
                "show_results": False,
                "created_at": datetime.now().isoformat()
            }
            self._write_data(default_data)
    
    def _read_data(self):
        """Read data from file with thread safety"""
        with self.lock:
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                # If file is corrupted or missing, recreate with defaults
                default_data = {
                    "participants": {},
                    "teams": ["팀 1"],
                    "votes": {},
                    "show_results": False,
                    "created_at": datetime.now().isoformat()
                }
                self._write_data(default_data)
                return default_data
    
    def _write_data(self, data):
        """Write data to file with thread safety"""
        with self.lock:
            data["updated_at"] = datetime.now().isoformat()
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_participants(self):
        """Get all participants"""
        data = self._read_data()
        return data.get("participants", {})
    
    def add_participant(self, email, team=None):
        """Add a participant"""
        data = self._read_data()
        data["participants"][email] = {
            "team": team,
            "added_at": datetime.now().isoformat()
        }
        self._write_data(data)
    
    def remove_participant(self, email):
        """Remove a participant"""
        data = self._read_data()
        if email in data["participants"]:
            del data["participants"][email]
            self._write_data(data)
    
    def assign_team(self, email, team):
        """Assign team to participant"""
        data = self._read_data()
        if email in data["participants"]:
            data["participants"][email]["team"] = team
            self._write_data(data)
    
    def get_teams(self):
        """Get all teams"""
        data = self._read_data()
        return data.get("teams", ["팀 1"])
    
    def update_teams(self, teams):
        """Update teams list"""
        data = self._read_data()
        data["teams"] = teams
        
        # Clean up team assignments for deleted teams
        for email, participant in data["participants"].items():
            if participant.get("team") not in teams:
                participant["team"] = None
        
        self._write_data(data)
    
    def get_votes(self):
        """Get all votes"""
        data = self._read_data()
        return data.get("votes", {})
    
    def cast_vote(self, email_hash, selected_teams):
        """Cast a vote"""
        data = self._read_data()
        data["votes"][email_hash] = {
            "teams": selected_teams,
            "voted_at": datetime.now().isoformat()
        }
        self._write_data(data)
    
    def has_voted(self, email_hash):
        """Check if user has voted"""
        data = self._read_data()
        return email_hash in data.get("votes", {})
    
    def get_show_results(self):
        """Get results display status"""
        data = self._read_data()
        return data.get("show_results", False)
    
    def set_show_results(self, show):
        """Set results display status"""
        data = self._read_data()
        data["show_results"] = show
        self._write_data(data)
    
    def get_user_team(self, email):
        """Get team for specific user"""
        participants = self.get_participants()
        return participants.get(email, {}).get("team")
    
    def is_email_registered(self, email):
        """Check if email is registered"""
        participants = self.get_participants()
        return email in participants
    
    def clear_all_data(self):
        """Clear all data (admin function)"""
        default_data = {
            "participants": {},
            "teams": ["팀 1"],
            "votes": {},
            "show_results": False,
            "created_at": datetime.now().isoformat()
        }
        self._write_data(default_data)
    
    def get_voting_stats(self):
        """Get voting statistics"""
        participants = self.get_participants()
        votes = self.get_votes()
        
        total_participants = len(participants)
        total_voted = len(votes)
        total_not_voted = total_participants - total_voted
        
        return {
            "total_participants": total_participants,
            "total_voted": total_voted,
            "total_not_voted": total_not_voted,
            "participation_rate": (total_voted / total_participants * 100) if total_participants > 0 else 0
        }
    
    def get_team_stats(self):
        """Get team statistics"""
        participants = self.get_participants()
        teams = self.get_teams()
        
        team_counts = {}
        unassigned_count = 0
        
        for team in teams:
            team_counts[team] = 0
        
        for participant in participants.values():
            team = participant.get("team")
            if team and team in team_counts:
                team_counts[team] += 1
            else:
                unassigned_count += 1
        
        return {
            "team_counts": team_counts,
            "unassigned_count": unassigned_count
        }
    
    def get_results_data(self):
        """Get formatted results data"""
        votes = self.get_votes()
        teams = self.get_teams()
        
        # Count votes for each team
        team_votes = {}
        for team in teams:
            team_votes[team] = 0
        
        for vote in votes.values():
            for team in vote.get("teams", []):
                if team in team_votes:
                    team_votes[team] += 1
        
        # Sort teams by vote count
        sorted_teams = sorted(team_votes.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "team_votes": team_votes,
            "sorted_results": sorted_teams,
            "total_votes": len(votes)
        }