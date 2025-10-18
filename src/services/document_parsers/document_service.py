"""
Document Parser Service
Unified interface for parsing various document formats
"""
from typing import Dict, Any, Optional
import os
import logging
from .pdf_parser import PDFParser
from .word_parser import WordParser
from .excel_parser import ExcelParser
from .powerpoint_parser import PowerPointParser

logger = logging.getLogger(__name__)


class DocumentParserService:
    """
    Unified service for parsing different document types
    Automatically detects file type and uses appropriate parser
    """
    
    # Supported file extensions and their parsers
    PARSERS = {
        '.pdf': PDFParser,
        '.docx': WordParser,
        '.doc': WordParser,  # Note: python-docx only supports .docx
        '.xlsx': ExcelParser,
        '.xls': ExcelParser,  # Note: openpyxl only supports .xlsx
        '.pptx': PowerPointParser,
        '.ppt': PowerPointParser,  # Note: python-pptx only supports .pptx
    }
    
    @classmethod
    def parse_document(cls, file_path: str, file_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Parse a document file and extract its content
        
        Args:
            file_path: Path to the document file
            file_type: Optional file extension (auto-detected if not provided)
            
        Returns:
            Dictionary containing parsed content and metadata
        """
        try:
            # Determine file type
            if not file_type:
                _, file_type = os.path.splitext(file_path)
                file_type = file_type.lower()
            
            # Check if file type is supported
            if file_type not in cls.PARSERS:
                return {
                    'success': False,
                    'error': f'Unsupported file type: {file_type}',
                    'supported_types': list(cls.PARSERS.keys()),
                    'text': '',
                    'file_type': file_type
                }
            
            # Get appropriate parser
            parser_class = cls.PARSERS[file_type]
            
            # Parse the document
            logger.info(f"Parsing {file_type} file: {file_path}")
            parsed_data = parser_class.parse(file_path)
            
            # Add file type and summary
            parsed_data['file_type'] = file_type
            parsed_data['file_name'] = os.path.basename(file_path)
            
            if parsed_data.get('success'):
                parsed_data['summary'] = parser_class.get_summary(parsed_data)
            
            return parsed_data
            
        except Exception as e:
            logger.error(f"Error in document parser service: {e}")
            return {
                'success': False,
                'error': str(e),
                'text': '',
                'file_type': file_type or 'unknown'
            }
    
    @classmethod
    def get_ai_context(cls, parsed_data: Dict[str, Any], max_length: int = 8000) -> str:
        """
        Generate AI-friendly context from parsed document
        Truncates content if too long to fit in AI context window
        
        Args:
            parsed_data: Output from parse_document()
            max_length: Maximum character length for AI context
            
        Returns:
            Formatted string suitable for AI context
        """
        if not parsed_data.get('success'):
            return f"Document parsing failed: {parsed_data.get('error', 'Unknown error')}"
        
        context_parts = []
        
        # Add document summary
        if parsed_data.get('summary'):
            context_parts.append("=== DOCUMENT SUMMARY ===")
            context_parts.append(parsed_data['summary'])
            context_parts.append("")
        
        # Add metadata
        metadata = parsed_data.get('metadata', {})
        if metadata:
            context_parts.append("=== METADATA ===")
            for key, value in metadata.items():
                if value and key not in ['sheet_width', 'slide_width', 'slide_height']:
                    context_parts.append(f"{key.replace('_', ' ').title()}: {value}")
            context_parts.append("")
        
        # Add main content
        text = parsed_data.get('text', '')
        if text:
            context_parts.append("=== CONTENT ===")
            
            # Truncate if necessary
            remaining_length = max_length - len('\n'.join(context_parts))
            if len(text) > remaining_length:
                text = text[:remaining_length] + "\n\n... (content truncated)"
            
            context_parts.append(text)
        
        return '\n'.join(context_parts)
    
    @classmethod
    def is_supported(cls, file_extension: str) -> bool:
        """
        Check if a file type is supported
        
        Args:
            file_extension: File extension (e.g., '.pdf', '.docx')
            
        Returns:
            True if supported, False otherwise
        """
        return file_extension.lower() in cls.PARSERS
    
    @classmethod
    def get_supported_types(cls) -> list:
        """
        Get list of supported file types
        
        Returns:
            List of supported file extensions
        """
        return list(cls.PARSERS.keys())
    
    @classmethod
    def get_file_type_description(cls, file_extension: str) -> str:
        """
        Get human-readable description of file type
        
        Args:
            file_extension: File extension
            
        Returns:
            Description string
        """
        descriptions = {
            '.pdf': 'PDF Document',
            '.docx': 'Word Document',
            '.doc': 'Word Document (Legacy)',
            '.xlsx': 'Excel Spreadsheet',
            '.xls': 'Excel Spreadsheet (Legacy)',
            '.pptx': 'PowerPoint Presentation',
            '.ppt': 'PowerPoint Presentation (Legacy)'
        }
        return descriptions.get(file_extension.lower(), 'Unknown Document Type')

