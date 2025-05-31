import logging

logger = logging.getLogger(__name__)

class TextProcessor:
    """Handles text input processing and validation."""
    
    @staticmethod
    def process_text(text):
        """
        Process and validate raw text input.
        
        Args:
            text (str): Raw text input
            
        Returns:
            str: Cleaned and processed text
            
        Raises:
            ValueError: If text is invalid or too short
        """
        if not text or not isinstance(text, str):
            raise ValueError("Text input cannot be empty")
        
        # Clean the text
        cleaned_text = text.strip()
        
        if len(cleaned_text) < 50:
            raise ValueError("Text must be at least 50 characters long for meaningful summarization")
        
        if len(cleaned_text) > 50000:
            raise ValueError("Text is too long (maximum 50,000 characters)")
        
        logger.info(f"Processing text input of {len(cleaned_text)} characters")
        
        return cleaned_text
    
    @staticmethod
    def validate_text_length(text, min_length=50, max_length=50000):
        """
        Validate text length constraints.
        
        Args:
            text (str): Text to validate
            min_length (int): Minimum character length
            max_length (int): Maximum character length
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not text:
            return False
        
        length = len(text.strip())
        return min_length <= length <= max_length
