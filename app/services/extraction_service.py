# In app/services/extraction_service.py
# Correct the import to get models from the CORE module
from app.core.models import ExtractedData  # This is the correct import
import spacy
from typing import List
#from .models import ExtractedData
import logging

logger = logging.getLogger(__name__)

# Load the spaCy model. Using a small, efficient model for speed.
# Consider en_core_web_md for better accuracy if performance allows.
nlp = spacy.load("en_core_web_sm")

# Define a list of relevant skills keywords. This should be expanded significantly.
SKILLS_KEYWORDS = {
    "python", "javascript", "java", "html", "css", "react", "node.js",
    "sql", "nosql", "mongodb", "aws", "docker", "kubernetes", "git",
    "machine learning", "data analysis", "project management",
    "digital marketing", "ui/ux", "figma"
}

class ExtractionService:
    """Service for extracting features from raw text using NLP."""

    @staticmethod
    def extract_skills(text: str) -> List[str]:
        """Extract skills by matching against a keywords list and NER."""
        doc = nlp(text.lower())
        found_skills = set()

        # Check for matches with our skills list
        for token in doc:
            if token.text in SKILLS_KEYWORDS:
                found_skills.add(token.text)

        # Also use Entity Recognition to find potential skills
        for ent in doc.ents:
            if ent.label_ == "ORG" and ent.text.lower() in SKILLS_KEYWORDS: # e.g., "AWS"
                found_skills.add(ent.text.lower())
        return list(found_skills)

    @staticmethod
    def extract_education(text: str) -> List[str]:
        """Extract education information using pattern matching."""
        doc = nlp(text)
        education_entries = []
        # Look for education-related keywords
        for sent in doc.sents:
            if any(word in sent.text.lower() for word in ['b.sc', 'bachelor', 'degree', 'university', 'polytechnic', 'ond', 'hnd']):
                education_entries.append(sent.text.strip())
        return education_entries

    def extract_all(self, raw_text: str) -> ExtractedData:
        """Orchestrates the extraction of all data points."""
        try:
            skills = self.extract_skills(raw_text)
            education = self.extract_education(raw_text)
            # Experience extraction is more complex. For V1, we can return the raw text or use simple regex.
            # For now, we'll skip deep experience parsing.

            return ExtractedData(
                raw_text=raw_text,
                skills=skills,
                education=education,
                experience=None
            )
        except Exception as e:
            logger.error(f"Error during text extraction: {e}")
            raise

# Global instance
extraction_service = ExtractionService()