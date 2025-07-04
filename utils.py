import re
import ipaddress

def is_valid_bin(bin_number):
    """
    Validate if the input is a valid BIN number or card number.
    
    Args:
        bin_number (str): BIN number or card number to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not bin_number:
        return False
    
    # Check if it's a 6-digit BIN or a full card number (13-19 digits)
    return bool(re.match(r'^\d{6,19}$', bin_number))

def is_valid_ip(ip_address):
    """
    Validate if the input is a valid IP address.
    
    Args:
        ip_address (str): IP address to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        ipaddress.ip_address(ip_address)
        return True
    except ValueError:
        return False

def is_valid_url(url):
    """
    Validate if the input is a valid URL.
    
    Args:
        url (str): URL to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    url_pattern = re.compile(
        r'^(?:http|https)://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return bool(url_pattern.match(url))

def classify_risk(is_3ds, fraud_context):
    """
    Classify the risk level of a BIN based on 3DS status and context.
    
    Args:
        is_3ds (bool): Whether 3DS is enforced
        fraud_context (bool): Whether the BIN was found in a fraud context
        
    Returns:
        str: Risk classification (Enforced, Weak, Unsafe)
    """
    if is_3ds:
        return "Enforced"
    elif fraud_context:
        return "Unsafe"
    else:
        return "Weak"

def get_risk_icon(risk_level):
    """
    Get the appropriate icon for a risk level.
    
    Args:
        risk_level (str): Risk classification
        
    Returns:
        str: Icon representing the risk level
    """
    if risk_level == "Enforced":
        return "✅"
    elif risk_level == "Weak":
        return "⚠️"
    else:  # Unsafe
        return "❌"
