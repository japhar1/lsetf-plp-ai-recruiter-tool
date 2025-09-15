import logging
from typing import List, Dict
from app.core.models import CandidateProfile, RankingCriteria

logger = logging.getLogger(__name__)

class RankingService:
    """Service for ranking candidates based on extracted data."""
    
    def __init__(self, criteria: RankingCriteria = None):
        self.criteria = criteria or RankingCriteria()
    
    def calculate_skills_score(self, skills: List[str]) -> float:
        """Calculate score based on skills matching."""
        if not skills:
            return 0.0
        
        # Bonus for required skills
        required_skills_matched = [
            skill for skill in skills 
            if skill.lower() in [rs.lower() for rs in self.criteria.required_skills]
        ]
        
        # Base score is percentage of skills found relative to some expectation
        base_score = min(len(skills) / 10.0, 1.0)  # Cap at 1.0 (10+ skills)
        
        # Add bonus for required skills
        required_bonus = len(required_skills_matched) * 0.2
        
        return min(base_score + required_bonus, 1.0)
    
    def calculate_education_score(self, education: List[str]) -> float:
        """Calculate score based on education level."""
        if not education:
            return 0.0
        
        score = 0.0
        education_text = " ".join(education).lower()
        
        # Simple heuristic scoring
        if any(term in education_text for term in ['phd', 'doctorate']):
            score = 1.0
        elif any(term in education_text for term in ['master', 'msc', 'mba']):
            score = 0.8
        elif any(term in education_text for term in ['bachelor', 'b.sc', 'undergraduate']):
            score = 0.6
        elif any(term in education_text for term in ['diploma', 'certificate', 'ond', 'hnd']):
            score = 0.4
        
        return score
    
    def calculate_experience_score(self, experience_text: str) -> float:
        """Calculate score based on experience (simple version)."""
        if not experience_text:
            return 0.0
        
        # Simple heuristic: look for years of experience patterns
        text_lower = experience_text.lower()
        score = 0.0
        
        # Very basic experience detection
        if any(term in text_lower for term in ['year', 'yr', 'experience']):
            # This is a placeholder - real implementation would parse years
            score = 0.7  # Assume some experience
        
        return score
    
    def score_candidate(self, profile: CandidateProfile) -> CandidateProfile:
        """Calculate overall score for a candidate."""
        breakdown = {}
        
        # Calculate individual scores
        skills_score = self.calculate_skills_score(profile.extracted_data.skills)
        education_score = self.calculate_education_score(profile.extracted_data.education)
        experience_score = self.calculate_experience_score(profile.extracted_data.experience or "")
        
        # Store breakdown
        breakdown['skills'] = skills_score
        breakdown['education'] = education_score
        breakdown['experience'] = experience_score
        
        # Calculate weighted total
        total_score = (
            skills_score * self.criteria.skills_weight +
            education_score * self.criteria.education_weight +
            experience_score * self.criteria.experience_weight
        )
        
        # Update profile
        profile.score = total_score
        profile.score_breakdown = breakdown
        
        return profile
    
    def rank_candidates(self, profiles: List[CandidateProfile]) -> List[CandidateProfile]:
        """Rank multiple candidates by their scores."""
        scored_profiles = [self.score_candidate(profile) for profile in profiles]
        return sorted(scored_profiles, key=lambda x: x.score, reverse=True)

# Global instance
ranking_service = RankingService()