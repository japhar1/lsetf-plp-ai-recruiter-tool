#!/usr/bin/env python3
"""
Simple test script to verify the parsing and extraction services work.
Run this from the project root directory:
    python scripts/test_parsing.py
"""
import sys
from pathlib import Path

# Add the project root to Python path so we can import 'app'
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Now we can import our modules
from app.services.parser_service import parser_service
from app.services.extraction_service import extraction_service

def main():
    """Test the parsing and extraction pipeline."""
    # Path to the sample resume
    test_file = Path("data") / "sample_cv.pdf"
    
    if not test_file.exists():
        print(f"❌ ERROR: Please add a sample PDF resume at: {test_file}")
        return

    print("1. Parsing file...")
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

    print("\n🎉 All tests passed! Core engine is working.")

if __name__ == "__main__":
    main()