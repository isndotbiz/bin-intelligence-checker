import re
import requests
from bs4 import BeautifulSoup
from bin_checker import check_bin_3ds
from utils import classify_risk, is_valid_url

def scrape_bins_from_url(url, ip_address=None):
    """
    Scrape a URL for potential BIN numbers and check their 3DS status.
    
    Args:
        url (str): URL to scrape
        ip_address (str, optional): IP address to use for 3DS lookups, can be None
        
    Returns:
        list: List of dictionaries containing BIN information
    """
    if not is_valid_url(url):
        return "Invalid URL format. Please provide a valid URL."
    
    try:
        # Make request to the URL
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return f"Failed to access URL. Status code: {response.status_code}"
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract all text content
        text_content = soup.get_text()
        
        # Find all potential BIN numbers (6 digits)
        bin_pattern = r'\b\d{6}\b'
        potential_bins = set(re.findall(bin_pattern, text_content))
        
        if not potential_bins:
            return []
        
        # Check each BIN (limit to 15 to avoid excessive API calls)
        results = []
        for bin_number in list(potential_bins)[:15]:
            result = check_bin_3ds(bin_number, ip_address)
            
            # Skip if the API call failed
            if "error" in result:
                continue
                
            # Determine if this is from a potentially fraudulent context
            fraud_context = is_fraud_context(url, text_content)
            
            # Classify risk level
            risk_level = classify_risk(result.get("is3DS", False), fraud_context)
            
            bin_data = {
                "BIN": bin_number,
                "Country": result.get("country", "Unknown"),
                "Scheme": result.get("scheme", "Unknown"),
                "Issuer": result.get("issuer", "Unknown"),
                "is3DS": result.get("is3DS", False),
                "Risk Level": risk_level
            }
            
            results.append(bin_data)
        
        return results
    
    except Exception as e:
        return f"Error scraping URL: {str(e)}"

def is_fraud_context(url, content):
    """
    Simple heuristic to determine if the context might be related to fraud.
    
    Args:
        url (str): URL of the scraped content
        content (str): Text content from the page
        
    Returns:
        bool: True if the context appears to be related to fraud
    """
    # Check URL for suspicious terms
    suspicious_domains = [
        'pastebin', 'darkweb', 'hack', 'crack', 'carding', 'cvv',
        'dumps', 'fraud', 'stolen', 'breach', 'leak'
    ]
    
    if any(term in url.lower() for term in suspicious_domains):
        return True
    
    # Check content for suspicious terms
    suspicious_terms = [
        'cvv', 'fullz', 'dumps', 'cashout', 'carding', 'fraud',
        'stolen credit card', 'hacked', 'leaked', 'unauthorized',
        'darknet', 'darkweb', 'carder', 'skimmer'
    ]
    
    content_lower = content.lower()
    if any(term in content_lower for term in suspicious_terms):
        return True
    
    # Check for high density of credit card related terms
    cc_terms = ['card', 'credit', 'debit', 'visa', 'mastercard', 'amex', 'bin', 'cvv', 'exp']
    term_count = sum(content_lower.count(term) for term in cc_terms)
    
    # If there are many card-related terms, it might be suspicious
    if term_count > 15:
        return True
    
    return False
