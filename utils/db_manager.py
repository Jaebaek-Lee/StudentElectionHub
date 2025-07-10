import os
import hashlib
from datetime import datetime
from sqlalchemy import create_engine, Column, String, DateTime, Boolean, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json

Base = declarative_base()

class Participant(Base):
    __tablename__ = 'participants'
    
    email = Column(String, primary_key=True)
    team = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

class Team(Base):
    __tablename__ = 'teams'
    
    name = Column(String, primary_key=True)
    created_at = Column(DateTime, default=datetime.now)

class Vote(Base):
    __tablename__ = 'votes'
    
    email_hash = Column(String, primary_key=True)
    selected_teams = Column(Text)  # JSON string
    voted_at = Column(DateTime, default=datetime.now)

class Settings(Base):
    __tablename__ = 'settings'
    
    key = Column(String, primary_key=True)
    value = Column(String)
    updated_at = Column(DateTime, default=datetime.now)

class DatabaseManager:
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not found")
        
        self.engine = create_engine(self.database_url)
        
        # Create tables if they don't exist
        try:
            Base.metadata.create_all(self.engine)
        except Exception as e:
            # Tables might already exist, ignore the error
            pass
        
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
        # Initialize default data
        self.initialize_default_data()
    
    def initialize_default_data(self):
        """Initialize default data if not exists"""
        # Create default team if no teams exist
        if not self.session.query(Team).first():
            default_team = Team(name="팀 1")
            self.session.add(default_team)
        
        # Set default settings
        if not self.session.query(Settings).filter_by(key='show_results').first():
            show_results = Settings(key='show_results', value='false')
            self.session.add(show_results)
        
        self.session.commit()
    
    def add_participant(self, email, team=None):
        """Add a participant"""
        existing = self.session.query(Participant).filter_by(email=email).first()
        if not existing:
            participant = Participant(email=email, team=team)
            self.session.add(participant)
            self.session.commit()
            return True
        return False
    
    def remove_participant(self, email):
        """Remove a participant"""
        participant = self.session.query(Participant).filter_by(email=email).first()
        if participant:
            self.session.delete(participant)
            self.session.commit()
            return True
        return False
    
    def assign_team(self, email, team):
        """Assign team to participant"""
        participant = self.session.query(Participant).filter_by(email=email).first()
        if participant:
            participant.team = team
            self.session.commit()
            return True
        return False
    
    def get_participants(self):
        """Get all participants"""
        participants = self.session.query(Participant).all()
        return {p.email: {'team': p.team, 'created_at': p.created_at.isoformat()} 
                for p in participants}
    
    def get_teams(self):
        """Get all teams"""
        teams = self.session.query(Team).all()
        return [t.name for t in teams]
    
    def add_team(self, team_name):
        """Add a new team"""
        existing = self.session.query(Team).filter_by(name=team_name).first()
        if not existing:
            team = Team(name=team_name)
            self.session.add(team)
            self.session.commit()
            return True
        return False
    
    def remove_team(self, team_name):
        """Remove a team"""
        team = self.session.query(Team).filter_by(name=team_name).first()
        if team:
            # Remove team assignments for this team
            participants = self.session.query(Participant).filter_by(team=team_name).all()
            for p in participants:
                p.team = None
            
            self.session.delete(team)
            self.session.commit()
            return True
        return False
    
    def update_teams(self, teams):
        """Update teams list"""
        # Get current teams
        current_teams = set(self.get_teams())
        new_teams = set(teams)
        
        # Remove deleted teams
        to_remove = current_teams - new_teams
        for team in to_remove:
            self.remove_team(team)
        
        # Add new teams
        to_add = new_teams - current_teams
        for team in to_add:
            self.add_team(team)
    
    def cast_vote(self, email_hash, selected_teams):
        """Cast a vote"""
        existing = self.session.query(Vote).filter_by(email_hash=email_hash).first()
        if not existing:
            vote = Vote(
                email_hash=email_hash, 
                selected_teams=json.dumps(selected_teams)
            )
            self.session.add(vote)
            self.session.commit()
            return True
        return False
    
    def has_voted(self, email_hash):
        """Check if user has voted"""
        vote = self.session.query(Vote).filter_by(email_hash=email_hash).first()
        return vote is not None
    
    def get_votes(self):
        """Get all votes"""
        votes = self.session.query(Vote).all()
        return {v.email_hash: {
            'teams': json.loads(v.selected_teams),
            'voted_at': v.voted_at.isoformat()
        } for v in votes}
    
    def get_user_team(self, email):
        """Get team for specific user"""
        participant = self.session.query(Participant).filter_by(email=email).first()
        return participant.team if participant else None
    
    def is_email_registered(self, email):
        """Check if email is registered"""
        participant = self.session.query(Participant).filter_by(email=email).first()
        return participant is not None
    
    def get_show_results(self):
        """Get results display status"""
        setting = self.session.query(Settings).filter_by(key='show_results').first()
        return setting.value.lower() == 'true' if setting else False
    
    def set_show_results(self, show):
        """Set results display status"""
        setting = self.session.query(Settings).filter_by(key='show_results').first()
        if setting:
            setting.value = 'true' if show else 'false'
            setting.updated_at = datetime.now()
        else:
            setting = Settings(key='show_results', value='true' if show else 'false')
            self.session.add(setting)
        
        self.session.commit()
    
    def get_voting_stats(self):
        """Get voting statistics"""
        total_participants = self.session.query(Participant).count()
        total_votes = self.session.query(Vote).count()
        
        return {
            "total_participants": total_participants,
            "total_voted": total_votes,
            "total_not_voted": total_participants - total_votes,
            "participation_rate": (total_votes / total_participants * 100) if total_participants > 0 else 0
        }
    
    def get_team_stats(self):
        """Get team statistics"""
        teams = self.get_teams()
        team_counts = {}
        
        for team in teams:
            count = self.session.query(Participant).filter_by(team=team).count()
            team_counts[team] = count
        
        unassigned_count = self.session.query(Participant).filter(Participant.team.is_(None)).count()
        
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
    
    def clear_all_data(self):
        """Clear all data (admin function)"""
        self.session.query(Vote).delete()
        self.session.query(Participant).delete()
        self.session.query(Team).delete()
        self.session.query(Settings).delete()
        self.session.commit()
        
        # Reinitialize default data
        self.initialize_default_data()
    
    def __del__(self):
        """Close session when object is destroyed"""
        if hasattr(self, 'session'):
            self.session.close()