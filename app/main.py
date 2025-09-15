from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pathlib import Path
import uuid
import tempfile
import shutil

from app.services.parser_service import parser_service
from app.services.extraction_service import extraction_service
from app.services.ranking_service import ranking_service
from app.core.models import CandidateProfile, RankingCriteria

app = FastAPI(
    title="LSETF AI Recruitment API",
    description="AI-powered candidate ranking system for LSETF/PLP programs",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Default ranking criteria for LSETF programs
DEFAULT_CRITERIA = RankingCriteria(
    skills_weight=0.5,
    experience_weight=0.3,
    education_weight=0.2,
    required_skills=['python', 'javascript', 'sql', 'react', 'node.js', 'aws']
)

@app.get("/")
async def root():
    return {"message": "LSETF AI Recruitment API - Ready for candidate evaluation"}

@app.post("/api/analyze-candidate")
async def analyze_candidate(file: UploadFile = File(...)):
    """
    Analyze a single candidate's resume and return a score.
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.pdf', '.docx', '.doc')):
            raise HTTPException(status_code=400, detail="Only PDF and Word documents are supported")
        
        # Save uploaded file temporarily
        file_extension = Path(file.filename).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_path = Path(temp_file.name)
        
        try:
            # Process the file
            raw_text = parser_service.parse_file(temp_path)
            extracted_data = extraction_service.extract_all(raw_text)
            
            # Create candidate profile
            candidate_profile = CandidateProfile(
                candidate_id=str(uuid.uuid4()),
                extracted_data=extracted_data
            )
            
            # Score the candidate
            ranking_service.criteria = DEFAULT_CRITERIA
            scored_profile = ranking_service.score_candidate(candidate_profile)
            
            # Clean up temp file
            temp_path.unlink()
            
            return {
                "success": True,
                "candidate_id": scored_profile.candidate_id,
                "score": scored_profile.score,
                "score_breakdown": scored_profile.score_breakdown,
                "extracted_data": {
                    "skills": scored_profile.extracted_data.skills,
                    "education": scored_profile.extracted_data.education,
                    "experience_available": scored_profile.extracted_data.experience is not None
                }
            }
            
        except Exception as e:
            temp_path.unlink()  # Clean up on error
            raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.post("/api/analyze-batch")
async def analyze_batch(files: list[UploadFile] = File(...)):
    """
    Analyze multiple candidates and return ranked results.
    """
    try:
        candidates = []
        
        for file in files:
            # Validate file type
            if not file.filename.lower().endswith(('.pdf', '.docx', '.doc')):
                continue  # Skip invalid files
            
            # Save uploaded file temporarily
            file_extension = Path(file.filename).suffix
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                shutil.copyfileobj(file.file, temp_file)
                temp_path = Path(temp_file.name)
            
            try:
                # Process the file
                raw_text = parser_service.parse_file(temp_path)
                extracted_data = extraction_service.extract_all(raw_text)
                
                # Create candidate profile
                candidate_profile = CandidateProfile(
                    candidate_id=f"{Path(file.filename).stem}_{str(uuid.uuid4())[:8]}",
                    extracted_data=extracted_data
                )
                
                candidates.append(candidate_profile)
                
            except Exception as e:
                print(f"Error processing {file.filename}: {e}")
            finally:
                # Clean up temp file
                try:
                    temp_path.unlink()
                except:
                    pass
        
        # Rank all candidates
        ranking_service.criteria = DEFAULT_CRITERIA
        ranked_candidates = ranking_service.rank_candidates(candidates)
        
        # Prepare response
        results = []
        for rank, candidate in enumerate(ranked_candidates, 1):
            results.append({
                "rank": rank,
                "candidate_id": candidate.candidate_id,
                "score": candidate.score,
                "score_breakdown": candidate.score_breakdown,
                "skills": candidate.extracted_data.skills,
                "education_snippets": candidate.extracted_data.education[:3]  # First 3 snippets
            })
        
        return {
            "success": True,
            "total_candidates": len(results),
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch processing error: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "service": "LSETF AI Recruitment API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)