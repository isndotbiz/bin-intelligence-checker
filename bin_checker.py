import os
import requests
import json

def check_bin_3ds(bin_number, ip_address=None):
    """
    Check the 3DS status of a BIN or full card number using the 3ds-lookup RapidAPI.
    
    Args:
        bin_number (str): Card number (can be 6-digit BIN or full card number)
        ip_address (str, optional): IP address for geolocation context
        
    Returns:
        dict: Response from the API containing 3DS information
    """
    # Generate a sample full card number from the BIN if it's just 6 digits
    # This is necessary because the API works with full card numbers, not just BINs
    card_number = bin_number
    if len(bin_number) == 6:
        # Append zeros to make it look like a full card number
        card_number = bin_number + "0000000000"
    
    # If IP is provided, use binip endpoint, otherwise use cards endpoint
    if ip_address:
        url = f"https://3ds-lookup.p.rapidapi.com/binip/?bin={bin_number}&ip={ip_address}"
    else:
        # Use cards endpoint per the API example
        url = f"https://3ds-lookup.p.rapidapi.com/cards/?num={card_number}"
    
    headers = {
        "X-RapidAPI-Key": "8683a24fbdmsh4ad4a4745be87d5p1e2a9ejsnf80157137a5c",
        "X-RapidAPI-Host": "3ds-lookup.p.rapidapi.com"
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        # Check if the request was successful
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": f"API request failed with status code {response.status_code}: {response.text}"
            }
    except Exception as e:
        return {
            "error": f"Request failed: {str(e)}"
        }
