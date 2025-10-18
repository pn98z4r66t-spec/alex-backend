"""
PDF Document Parser
Extracts text, metadata, and structure from PDF files
"""
import PyPDF2
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class PDFParser:
    """Parser for PDF documents"""
    
    @staticmethod
    def parse(file_path: str) -> Dict[str, Any]:
        """
        Parse PDF file and extract content
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dictionary containing:
                - text: Full text content
                - pages: List of page contents
                - metadata: Document metadata
                - page_count: Number of pages
                - has_images: Whether document contains images
        """
        try:
            result = {
                'text': '',
                'pages': [],
                'metadata': {},
                'page_count': 0,
                'has_images': False,
                'success': True,
                'error': None
            }
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Get page count
                result['page_count'] = len(pdf_reader.pages)
                
                # Extract metadata
                if pdf_reader.metadata:
                    result['metadata'] = {
                        'title': pdf_reader.metadata.get('/Title', ''),
                        'author': pdf_reader.metadata.get('/Author', ''),
                        'subject': pdf_reader.metadata.get('/Subject', ''),
                        'creator': pdf_reader.metadata.get('/Creator', ''),
                        'producer': pdf_reader.metadata.get('/Producer', ''),
                        'creation_date': str(pdf_reader.metadata.get('/CreationDate', '')),
                    }
                
                # Extract text from each page
                all_text = []
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    try:
                        page_text = page.extract_text()
                        result['pages'].append({
                            'page_number': page_num,
                            'text': page_text,
                            'char_count': len(page_text)
                        })
                        all_text.append(page_text)
                        
                        # Check for images (basic detection)
                        if '/XObject' in page.get('/Resources', {}):
                            result['has_images'] = True
                            
                    except Exception as e:
                        logger.warning(f"Error extracting text from page {page_num}: {e}")
                        result['pages'].append({
                            'page_number': page_num,
                            'text': '',
                            'error': str(e)
                        })
                
                # Combine all text
                result['text'] = '\n\n'.join(all_text)
                
                # Add summary statistics
                result['statistics'] = {
                    'total_characters': len(result['text']),
                    'total_words': len(result['text'].split()),
                    'pages_with_content': sum(1 for p in result['pages'] if p.get('text', '').strip()),
                }
                
            return result
            
        except Exception as e:
            logger.error(f"Error parsing PDF: {e}")
            return {
                'success': False,
                'error': str(e),
                'text': '',
                'pages': [],
                'metadata': {},
                'page_count': 0
            }
    
    @staticmethod
    def get_summary(parsed_data: Dict[str, Any]) -> str:
        """
        Generate a human-readable summary of the PDF
        
        Args:
            parsed_data: Output from parse() method
            
        Returns:
            Summary string
        """
        if not parsed_data.get('success'):
            return f"Failed to parse PDF: {parsed_data.get('error')}"
        
        summary_parts = []
        
        # Basic info
        summary_parts.append(f"PDF Document with {parsed_data['page_count']} pages")
        
        # Metadata
        metadata = parsed_data.get('metadata', {})
        if metadata.get('title'):
            summary_parts.append(f"Title: {metadata['title']}")
        if metadata.get('author'):
            summary_parts.append(f"Author: {metadata['author']}")
        
        # Statistics
        stats = parsed_data.get('statistics', {})
        if stats:
            summary_parts.append(
                f"Content: {stats.get('total_words', 0)} words, "
                f"{stats.get('total_characters', 0)} characters"
            )
        
        # Images
        if parsed_data.get('has_images'):
            summary_parts.append("Contains images/graphics")
        
        return '\n'.join(summary_parts)

