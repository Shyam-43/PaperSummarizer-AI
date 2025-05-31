import trafilatura
import logging
from urllib.parse import urlparse
import requests

logger = logging.getLogger(__name__)

class URLProcessor:
    """Handles URL content extraction and processing."""
    
    @staticmethod
    def extract_content_from_url(url):
        """
        Extract main text content from a URL.
        
        Args:
            url (str): URL to extract content from
            
        Returns:
            str: Extracted text content
            
        Raises:
            ValueError: If URL is invalid or content cannot be extracted
        """
        try:
            # Validate URL format
            if not URLProcessor.is_valid_url(url):
                raise ValueError("Invalid URL format")
            
            # Add protocol if missing
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            logger.info(f"Extracting content from URL: {url}")
            
            # Fetch and extract content using trafilatura
            downloaded = trafilatura.fetch_url(url)
            
            if not downloaded:
                raise ValueError("Could not fetch content from URL")
            
            text_content = trafilatura.extract(downloaded)
            
            if not text_content:
                raise ValueError("No readable content found on the webpage")
            
            # Clean and validate extracted text
            cleaned_text = text_content.strip()
            
            if len(cleaned_text) < 50:
                raise ValueError("Webpage contains insufficient text for summarization (minimum 50 characters)")
            
            logger.info(f"Extracted {len(cleaned_text)} characters from URL")
            return cleaned_text
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error accessing URL: {str(e)}")
            raise ValueError("Failed to access the URL. Please check the URL and try again.")
        except Exception as e:
            logger.error(f"Error processing URL: {str(e)}")
            raise ValueError(f"Failed to extract content from URL: {str(e)}")
    
    @staticmethod
    def is_valid_url(url):
        """
        Validate URL format.
        
        Args:
            url (str): URL to validate
            
        Returns:
            bool: True if valid URL, False otherwise
        """
        if not url or not isinstance(url, str):
            return False
        
        try:
            # Add protocol if missing for validation
            test_url = url
            if not url.startswith(('http://', 'https://')):
                test_url = 'https://' + url
            
            result = urlparse(test_url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    @staticmethod
    def get_domain_from_url(url):
        """
        Extract domain name from URL.
        
        Args:
            url (str): URL to extract domain from
            
        Returns:
            str: Domain name or original URL if extraction fails
        """
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            parsed = urlparse(url)
            return parsed.netloc
        except Exception:
            return url
