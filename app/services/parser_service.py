import pdfplumber
import docx2txt
import logging
from pathlib import Path
#from .models import ExtractedData
from app.core.models import ExtractedData

logger = logging.getLogger(__name__)

class ParserService:
    """Service dedicated to parsing text from various file formats."""

    @staticmethod
    def parse_pdf(file_path: Path) -> str:
        """Extracts text from a PDF file using pdfplumber."""
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            logger.error(f"Error parsing PDF {file_path}: {e}")
            raise
        return text.strip()

    @staticmethod
    def parse_docx(file_path: Path) -> str:
        """Extracts text from a DOCX file using docx2txt."""
        try:
            text = docx2txt.process(file_path)
        except Exception as e:
            logger.error(f"Error parsing DOCX {file_path}: {e}")
            raise
        return text.strip()

    def parse_file(self, file_path: Path) -> str:
        """Router method to parse a file based on its suffix."""
        if not file_path.exists():
            raise FileNotFoundError(f"The file {file_path} was not found.")

        if file_path.suffix.lower() == '.pdf':
            return self.parse_pdf(file_path)
        elif file_path.suffix.lower() in ['.docx', '.doc']:
            return self.parse_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")

# Global instance for easy import
parser_service = ParserService()