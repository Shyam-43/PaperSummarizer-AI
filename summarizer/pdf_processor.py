import PyPDF2
import logging
import os
from typing import List, Tuple

logger = logging.getLogger(__name__)

class PDFProcessor:
    """Handles PDF file processing and text extraction."""
    
    @staticmethod
    def extract_text_from_pdf(file_path):
        """
        Extract text content from a single PDF file.
        
        Args:
            file_path (str): Path to the PDF file
            
        Returns:
            str: Extracted text content
            
        Raises:
            ValueError: If PDF cannot be processed or contains no text
        """
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_content = ""
                
                # Extract text from all pages
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text_content += page.extract_text() + "\n"
                
                # Clean and validate extracted text
                cleaned_text = text_content.strip()
                
                if not cleaned_text:
                    raise ValueError("No text content found in PDF file")
                
                if len(cleaned_text) < 50:
                    raise ValueError("PDF contains insufficient text for summarization (minimum 50 characters)")
                
                logger.info(f"Extracted {len(cleaned_text)} characters from PDF")
                return cleaned_text
                
        except PyPDF2.errors.PdfReadError as e:
            logger.error(f"PDF read error: {str(e)}")
            raise ValueError("Invalid or corrupted PDF file")
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            raise ValueError(f"Failed to process PDF: {str(e)}")
    
    @staticmethod
    def process_batch_pdfs(file_paths):
        """
        Process multiple PDF files and extract text from each.
        
        Args:
            file_paths (list): List of paths to PDF files
            
        Returns:
            list: List of tuples (filename, extracted_text, success_status)
        """
        results = []
        
        for file_path in file_paths:
            filename = os.path.basename(file_path)
            try:
                text_content = PDFProcessor.extract_text_from_pdf(file_path)
                results.append((filename, text_content, True, None))
                logger.info(f"Successfully processed {filename}")
            except Exception as e:
                error_msg = str(e)
                results.append((filename, "", False, error_msg))
                logger.error(f"Failed to process {filename}: {error_msg}")
        
        return results
    
    @staticmethod
    def validate_pdf_file(file):
        """
        Validate uploaded PDF file.
        
        Args:
            file: Flask file upload object
            
        Returns:
            bool: True if valid PDF, False otherwise
        """
        if not file or not file.filename:
            return False
        
        # Check file extension
        if not file.filename.lower().endswith('.pdf'):
            return False
        
        # Check file size (max 10MB per PDF)
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)  # Reset file pointer
        
        if file_size > 10 * 1024 * 1024:  # 10MB limit
            return False
        
        return True
    
    @staticmethod
    def save_uploaded_file(file, upload_folder):
        """
        Save uploaded file to the upload folder.
        
        Args:
            file: Flask file upload object
            upload_folder (str): Path to upload directory
            
        Returns:
            str: Path to saved file
        """
        import uuid
        
        # Generate unique filename to avoid conflicts
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(upload_folder, unique_filename)
        
        file.save(file_path)
        return file_path
