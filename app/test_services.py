#!/usr/bin/env python3
"""
Test script for parser, extraction, and ranking services.
Run this from the PROJECT ROOT directory:
    python -m app.test_services
"""
import sys
from pathlib import Path

# Get the current directory (app/) and then its parent (project root)
current_dir = Path(__file__).parent
project_root = current_dir.parent

# Now we can construct absolute paths
data_dir = project_root / "data"

# Now import the services using absolute imports from the app package
from app.services.parser_service import parser_service
from app.services.extraction_service import extraction_service
from app.services.ranking_service import ranking_service
from app.core.models import CandidateProfile, RankingCriteria

def main():
    """Test the parsing, extraction, and ranking pipeline."""
    # Path to the sample resume
    test_file = data_dir / "sample_cv.pdf"
    
    if not test_file.exists():
        print(f"❌ ERROR: Please add a sample PDF resume at: {test_file}")
        print("Creating a simple test file for demonstration...")
        
        # Create a simple text file as a fallback for testing
        test_file = data_dir / "test_resume.txt"
        with open(test_file, 'w') as f:
            f.write("""
            JOHN DOE RESUME
            Skills: Python, JavaScript, SQL, Git, Project Management
            Education: Bachelor of Science in Computer Science, University of Lagos, 2021
            Experience: Software Developer at Tech Company (2021-Present)
            Developed web applications using Python and React.
            """)
        print(f"Created test file: {test_file}")

    print(f"1. Parsing file: {test_file}...")
    try:
        raw_text = parser_service.parse_file(test_file)
        print(f"✅ Success! Raw text length: {len(raw_text)} characters\n")
        # Print first 200 chars to preview
        print("Preview:", raw_text[:200] + "...\n")
    except Exception as e:
        print(f"❌ Failed to parse file: {e}")
        return

    print("2. Extracting features...")
    try:
        extracted_data = extraction_service.extract_all(raw_text)
        print(f"✅ Skills found: {extracted_data.skills}")
        print(f"✅ Education snippets: {extracted_data.education}")
        if extracted_data.experience:
            print(f"Experience: {extracted_data.experience}")
    except Exception as e:
        print(f"❌ Failed to extract features: {e}")
        return

    print("\n3. Testing ranking system...")
    try:
        # Create a test candidate profile from our extracted data
        test_profile = CandidateProfile(
            candidate_id="test_001",
            extracted_data=extracted_data
        )
        
        # Set up ranking criteria (customize these for LSETF/PLP needs)
        criteria = RankingCriteria(
            skills_weight=0.5,
            experience_weight=0.3,
            education_weight=0.2,
            required_skills=['python', 'javascript', 'sql']  # Skills LSETF/PLP programs value
        )
        
        # Initialize ranking service with our criteria
        ranking_service.criteria = criteria
        
        # Score the candidate
        ranked_profile = ranking_service.score_candidate(test_profile)
        
        print(f"✅ Candidate Score: {ranked_profile.score:.2f}/1.0")
        print(f"✅ Score Breakdown:")
        print(f"   - Skills: {ranked_profile.score_breakdown['skills']:.2f}")
        print(f"   - Education: {ranked_profile.score_breakdown['education']:.2f}")
        print(f"   - Experience: {ranked_profile.score_breakdown['experience']:.2f}")
        
        # Test with multiple candidates (simulated)
        print(f"\n4. Testing multiple candidate ranking...")
        
        # Create a second simulated candidate with different skills
        simulated_extracted_data = extracted_data.model_copy()
        simulated_extracted_data.skills = ['python', 'java', 'aws', 'docker']  # Different skill set
        
        test_profile_2 = CandidateProfile(
            candidate_id="test_002",
            extracted_data=simulated_extracted_data
        )
        
        # Score and rank both candidates
        ranked_profile_2 = ranking_service.score_candidate(test_profile_2)
        all_profiles = [ranked_profile, ranked_profile_2]
        
        ranked_profiles = ranking_service.rank_candidates(all_profiles)
        
        print(f"✅ Ranked Candidates:")
        for i, profile in enumerate(ranked_profiles, 1):
            print(f"   {i}. Candidate {profile.candidate_id}: {profile.score:.2f}")
            print(f"      Skills: {profile.extracted_data.skills}")
        
    except Exception as e:
        print(f"❌ Failed to rank candidates: {e}")
        import traceback
        traceback.print_exc()
        return

    print("\n🎉 All tests passed! Core engine with ranking is working.")

if __name__ == "__main__":
    main()