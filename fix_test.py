#!/usr/bin/env python3
"""
TEST THAT WORKS WITH YOUR CURRENT FILE STRUCTURE
"""
import sys
from pathlib import Path
import importlib.util

# Add current directory to path
sys.path.insert(0, str(Path.cwd()))

print("Testing import with your actual file names...")

# Load parser service (note the filename has 'services' not 'service')
parser_file = Path("app/services/parser_services.py")
print(f"Parser file exists: {parser_file.exists()}")

# Load extraction service
extraction_file = Path("app/services/extraction_service.py")
print(f"Extraction file exists: {extraction_file.exists()}")

if parser_file.exists() and extraction_file.exists():
    try:
        # Load parser service
        parser_spec = importlib.util.spec_from_file_location("parser_services", str(parser_file))
        parser_module = importlib.util.module_from_spec(parser_spec)
        parser_spec.loader.exec_module(parser_module)
        parser_service = parser_module.parser_service
        
        # Load extraction service
        extraction_spec = importlib.util.spec_from_file_location("extraction_service", str(extraction_file))
        extraction_module = importlib.util.module_from_spec(extraction_spec)
        extraction_spec.loader.exec_module(extraction_module)
        extraction_service = extraction_module.extraction_service
        
        print("✅ Successfully loaded both services!")
        
        # Test with a simple text
        test_text = """
        John Doe - Python Developer
        Skills: Python, JavaScript, SQL, Git, React
        Education: B.Sc Computer Science, University of Lagos
        Experience: 3 years as Software Developer
        """
        
        print("Testing extraction...")
        result = extraction_service.extract_all(test_text)
        print(f"Skills: {result.skills if hasattr(result, 'skills') else result.get('skills', 'N/A')}")
        print(f"Education: {result.education if hasattr(result, 'education') else result.get('education', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Error loading services: {e}")
        import traceback
        traceback.print_exc()
else:
    print("❌ Required files not found!")