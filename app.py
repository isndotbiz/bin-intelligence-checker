"""
BIN Intelligence & 3DS Enforcement Checker
A Streamlit application for analyzing BIN numbers and 3DS enforcement

This application provides comprehensive analysis of Bank Identification Numbers (BINs)
and 3D Secure (3DS) enforcement to help identify payment security risks.

Author: BIN Intelligence Project
Version: 1.0.0
License: MIT
"""

import streamlit as st
import pandas as pd
import re
import json
from bin_checker import check_bin_3ds
from bin_scraper import scrape_bins_from_url
from utils import classify_risk, is_valid_bin, is_valid_ip, is_valid_url, get_risk_icon
import database as db
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="BIN Intelligence & 3DS Enforcement Checker",
    page_icon="🔒",
    layout="wide"
)

# Initialize session state
if 'threshold_tracker' not in st.session_state:
    st.session_state.threshold_tracker = {}

if 'scraped_bins' not in st.session_state:
    st.session_state.scraped_bins = pd.DataFrame(
        columns=['BIN', 'Country', 'Scheme', 'Issuer', 'is3DS', 'Risk Level']
    )

# App title and description
st.title("🔒 BIN Intelligence & 3DS Enforcement Checker")

st.markdown("""
This tool performs BIN intelligence and 3DS enforcement checks to help identify potential payment fraud risks.
Enter a BIN (Bank Identification Number) or full card number to verify 3DS enforcement.

**Examples:**
- BIN: `411111` (Visa)
- BIN: `555555` (Mastercard)  
- Full Card: `4571730021788388` (for detailed analysis)
""")

# Display header section
st.markdown("---")
st.markdown("### 💳 Secure Payment Analysis Platform")
st.markdown("---")

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["BIN Checker", "URL Scraper", "Threshold Tracker", "Database History"])

with tab1:
    st.header("🔒 BIN & Card Analysis")
    
    # Input form
    with st.form(key="bin_check_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            bin_number = st.text_input("Enter BIN or Card Number", help="Enter 6-digit BIN or full card number for analysis")
        
        with col2:
            ip_address = st.text_input("Enter IP Address (optional, leave blank to skip)", 
                                       value="", 
                                       help="IP address for geolocation context")
        
        submit_button = st.form_submit_button(label="Check BIN")
    
    # Process form submission
    if submit_button:
        if not is_valid_bin(bin_number):
            st.error("Please enter a valid BIN number (6 digits) or full card number (13-19 digits).")
        elif ip_address and not is_valid_ip(ip_address):
            st.error("Please enter a valid IP address or leave the field blank.")
        else:
            # Use None if IP field is empty
            ip_to_use = ip_address if ip_address.strip() else None
            with st.spinner("Checking BIN details..."):
                try:
                    result = check_bin_3ds(bin_number, ip_to_use)
                    
                    if result.get("error"):
                        st.error(f"Error: {result['error']}")
                    else:
                        # Create two columns
                        col1, col2 = st.columns(2)
                        
                        # Display basic info in first column
                        with col1:
                            st.subheader("Card Information")
                            # Display the first 6 digits as BIN
                            bin_display = bin_number[:6] if len(bin_number) > 6 else bin_number
                            st.json({
                                "Input": bin_number,
                                "BIN": bin_display,
                                "Scheme": result.get("scheme", "Unknown"),
                                "Type": result.get("cardType", "Unknown"),
                                "Country": result.get("country", "Unknown"),
                                "Issuer": result.get("issuer", "Unknown"),
                                "IP Location": result.get("ipCountry", "Unknown") if ip_to_use else "N/A"
                            })
                        
                        # Display security info in second column
                        with col2:
                            st.subheader("Security Status")
                            is3ds = result.get("is3DS", False)
                            risk_level = classify_risk(is3ds, False)  # Not scraped from fraud context
                            
                            if is3ds:
                                st.success("✅ 3D Secure: Enforced")
                            else:
                                st.warning("⚠️ 3D Secure: Not Enforced")
                            
                            st.info(f"Risk Classification: {get_risk_icon(risk_level)} {risk_level}")
                            
                            # Store in threshold tracker
                            if bin_number not in st.session_state.threshold_tracker:
                                st.session_state.threshold_tracker[bin_number] = {
                                    "bin": bin_number,
                                    "is3DS": is3ds,
                                    "scheme": result.get("scheme", "Unknown"),
                                    "issuer": result.get("issuer", "Unknown"),
                                    "thresholds": {}
                                }
                            
                            # Save to database
                            try:
                                # Prepare data for database
                                bin_data = {
                                    "BIN": bin_number,
                                    "ip_address": ip_address,
                                    "Scheme": result.get("scheme", "Unknown"),
                                    "Type": result.get("cardType", "Unknown"),
                                    "Country": result.get("country", "Unknown"),
                                    "Issuer": result.get("issuer", "Unknown"),
                                    "IP Location": result.get("ipCountry", "Unknown"),
                                    "is3DS": is3ds,
                                    "Risk Level": risk_level,
                                    "fraud_context": False,
                                    "raw_response": result
                                }
                                
                                # Add to database
                                db.add_bin_record(bin_data, source='manual')
                            except Exception as e:
                                st.error(f"Error saving to database: {str(e)}")
                        
                        # Display full response
                        with st.expander("View Full API Response"):
                            st.json(result)
                            
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

with tab2:
    st.header("🔍 BIN Scraper")
    st.markdown("### Web Intelligence & BIN Discovery")
    
    st.markdown("""
    This tool scrapes webpages for potential BIN numbers and checks their 3DS enforcement status.
    Enter a URL to scan for 6-digit BIN numbers.
    
    ⚠️ **Note**: Only use this tool on websites where you have permission to scrape content.
    """)
    
    # Input form
    with st.form(key="url_scraper_form"):
        url = st.text_input("Enter URL to scrape", 
                            help="URL to scan for potential BIN numbers")
        
        ip_address = st.text_input("IP Address for 3DS Lookup (optional, leave blank to skip)", 
                                  value="",
                                  help="IP address used for 3DS lookups")
        
        submit_button = st.form_submit_button(label="Scrape URL")
    
    # Process form submission
    if submit_button:
        if not is_valid_url(url):
            st.error("Please enter a valid URL (e.g., https://example.com)")
        elif ip_address and not is_valid_ip(ip_address):
            st.error("Please enter a valid IP address or leave the field blank.")
        else:
            # Use None if IP field is empty
            ip_to_use = ip_address if ip_address.strip() else None
            with st.spinner("Scraping URL for BINs..."):
                try:
                    scraped_bins = scrape_bins_from_url(url, ip_to_use)
                    
                    if isinstance(scraped_bins, str):  # Error message
                        st.error(scraped_bins)
                    elif not scraped_bins:
                        st.info("No BIN numbers found on the provided URL.")
                    else:
                        # Create DataFrame for display
                        df = pd.DataFrame(scraped_bins)
                        
                        # Store in session state
                        st.session_state.scraped_bins = pd.concat([st.session_state.scraped_bins, df], ignore_index=True)
                        
                        # Save to database
                        saved_count = 0
                        for _, bin_row in df.iterrows():
                            try:
                                # Prepare data for database
                                bin_data = {
                                    "BIN": bin_row["BIN"],
                                    "ip_address": ip_address,
                                    "Scheme": bin_row["Scheme"],
                                    "Country": bin_row["Country"],
                                    "Issuer": bin_row["Issuer"],
                                    "is3DS": bin_row["is3DS"],
                                    "Risk Level": bin_row["Risk Level"],
                                    "fraud_context": bin_row.get("fraud_context", False),
                                    "raw_response": {}  # Simplified for scraped BINs
                                }
                                
                                # Add to database
                                db.add_bin_record(bin_data, source='scraper', source_url=url)
                                saved_count += 1
                            except Exception as e:
                                st.error(f"Error saving BIN {bin_row['BIN']} to database: {str(e)}")
                        
                        # Display results
                        st.success(f"Found {len(scraped_bins)} potential BIN numbers and saved {saved_count} to database")
                        
                        # Format table with colored risk levels
                        st.write("### Scraped BINs Analysis")
                        
                        # Styling function to color risk levels
                        def highlight_risk(val):
                            color_map = {
                                'Enforced': 'background-color: #d4edda',  # green
                                'Weak': 'background-color: #fff3cd',      # yellow
                                'Unsafe': 'background-color: #f8d7da'     # red
                            }
                            return color_map.get(val, '')
                        
                        # Apply styling and display table
                        styled_df = df.style.map(highlight_risk, subset=['Risk Level'])
                        st.dataframe(styled_df)
                        
                        # Add BINs to threshold tracker
                        for _, row in df.iterrows():
                            bin_num = row['BIN']
                            if bin_num not in st.session_state.threshold_tracker:
                                st.session_state.threshold_tracker[bin_num] = {
                                    "bin": bin_num,
                                    "is3DS": row['is3DS'],
                                    "scheme": row['Scheme'],
                                    "issuer": row['Issuer'],
                                    "thresholds": {}
                                }
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
    
    # Display all scraped BINs
    if not st.session_state.scraped_bins.empty:
        with st.expander("View All Previously Scraped BINs"):
            st.dataframe(st.session_state.scraped_bins)

with tab3:
    st.header("💰 Dollar Threshold Tracker")
    
    st.markdown("""
    Track whether 3DS is triggered at specific dollar thresholds for different BINs.
    Select a BIN and enter the dollar amount to record whether 3DS was triggered.
    """)
    
    if not st.session_state.threshold_tracker:
        st.info("No BINs have been checked yet. Use the BIN Checker or URL Scraper to add BINs.")
    else:
        # Select BIN
        bin_options = list(st.session_state.threshold_tracker.keys())
        selected_bin = st.selectbox("Select BIN", bin_options)
        
        bin_data = st.session_state.threshold_tracker[selected_bin]
        
        # Display BIN info
        st.write(f"**Scheme:** {bin_data['scheme']}")
        st.write(f"**Issuer:** {bin_data['issuer']}")
        st.write(f"**3DS Enforced by default:** {'Yes ✅' if bin_data['is3DS'] else 'No ⚠️'}")
        
        # Threshold entry form
        with st.form(key="threshold_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                amount = st.number_input("Dollar Amount", min_value=0.01, step=0.01, format="%.2f")
            
            with col2:
                triggered = st.radio("3DS Triggered at this amount?", ["Yes", "No"])
            
            submit_button = st.form_submit_button(label="Record Threshold")
        
        if submit_button:
            # Store threshold data in session state
            st.session_state.threshold_tracker[selected_bin]["thresholds"][str(amount)] = (triggered == "Yes")
            
            # Store threshold data in database
            try:
                # Add to database
                db.add_threshold_record(
                    bin_number=selected_bin,
                    amount=amount,
                    triggered=(triggered == "Yes")
                )
                st.success(f"Recorded: 3DS {'triggered' if triggered == 'Yes' else 'not triggered'} at ${amount:.2f} and saved to database")
            except Exception as e:
                st.error(f"Error saving threshold data to database: {str(e)}")
                st.success(f"Recorded: 3DS {'triggered' if triggered == 'Yes' else 'not triggered'} at ${amount:.2f} (only in session)")
        
        # Display threshold history
        try:
            # Get threshold data from database
            db_thresholds = db.get_threshold_records(selected_bin)
            
            if db_thresholds or bin_data["thresholds"]:
                st.write("### Threshold History")
                
                threshold_data = []
                
                # Add data from database
                for record in db_thresholds:
                    threshold_data.append({
                        "Amount": f"${float(record.amount):.2f}",
                        "3DS Triggered": "Yes ✅" if record.triggered else "No ⚠️",
                        "Date Recorded": record.recorded_at.strftime("%Y-%m-%d %H:%M"),
                        "Source": "Database"
                    })
                
                # Also add data from session (in case it hasn't been saved to DB yet)
                for amount, triggered in bin_data["thresholds"].items():
                    # Check if this is already in the data from DB to avoid duplicates
                    amount_str = f"${float(amount):.2f}"
                    if not any(d["Amount"] == amount_str for d in threshold_data):
                        threshold_data.append({
                            "Amount": amount_str,
                            "3DS Triggered": "Yes ✅" if triggered else "No ⚠️",
                            "Date Recorded": "Current Session",
                            "Source": "Session"
                        })
                
                threshold_df = pd.DataFrame(threshold_data)
                if not threshold_df.empty:
                    threshold_df = threshold_df.sort_values(by="Amount")
                    st.table(threshold_df)
            else:
                st.info("No threshold data recorded for this BIN yet.")
        except Exception as e:
            st.error(f"Error retrieving threshold data: {str(e)}")
            
            # Fallback to session state if database access fails
            if bin_data["thresholds"]:
                st.write("### Threshold History (Session Only)")
                
                threshold_data = []
                for amount, triggered in bin_data["thresholds"].items():
                    threshold_data.append({
                        "Amount": f"${float(amount):.2f}",
                        "3DS Triggered": "Yes ✅" if triggered else "No ⚠️"
                    })
                
                threshold_df = pd.DataFrame(threshold_data)
                threshold_df = threshold_df.sort_values(by="Amount")
                st.table(threshold_df)
            else:
                st.info("No threshold data recorded for this BIN yet.")

# Database History Tab
with tab4:
    st.header("📊 Database History")
    
    st.markdown("""
    View all BIN records stored in the database. This shows the history of all BINs checked or scraped.
    """)
    
    # Fetch records from database
    try:
        records = db.get_bin_records(limit=100)
        
        if records:
            # Convert records to DataFrame for display
            bin_records = []
            for record in records:
                # Try to parse raw_response to get more details
                raw_data = {}
                try:
                    if record.raw_response:
                        raw_data = json.loads(record.raw_response)
                except:
                    pass
                
                bin_records.append({
                    "BIN": record.bin_number,
                    "Date": record.checked_at.strftime("%Y-%m-%d %H:%M"),
                    "Scheme": record.scheme,
                    "Type": record.card_type or raw_data.get("cardType", "Unknown"),
                    "Country": record.country,
                    "IP/Location": record.ip_country or raw_data.get("ipCountry", "Unknown"),
                    "Issuer": record.issuer,
                    "3DS": "Yes ✅" if record.is_3ds else "No ⚠️",
                    "Risk Level": record.risk_level,
                    "Source": record.source,
                    "IP Address": record.ip_address,
                    "URL": record.source_url if record.source == 'scraper' else "N/A",
                    "Fraud Context": "Yes ⚠️" if record.fraud_context else "No"
                })
            
            # Create DataFrame
            bin_df = pd.DataFrame(bin_records)
            
            # Display filter options
            col1, col2, col3 = st.columns(3)
            with col1:
                scheme_filter = st.multiselect(
                    "Filter by Scheme",
                    options=sorted([x for x in bin_df["Scheme"].unique() if str(x) != "nan"]),
                    default=[]
                )
            
            with col2:
                risk_filter = st.multiselect(
                    "Filter by Risk Level",
                    options=sorted([x for x in bin_df["Risk Level"].unique() if str(x) != "nan"]),
                    default=[]
                )
                
            with col3:
                country_filter = st.multiselect(
                    "Filter by Country",
                    options=sorted([x for x in bin_df["Country"].unique() if str(x) != "nan" and x != "Unknown"]),
                    default=[]
                )
            
            # Search by BIN
            bin_search = st.text_input("Search by BIN", 
                                      placeholder="Enter full or partial BIN number")
            
            # Apply filters
            filtered_df = bin_df.copy()
            
            if scheme_filter:
                filtered_df = filtered_df[filtered_df["Scheme"].isin(scheme_filter)]
            if risk_filter:
                filtered_df = filtered_df[filtered_df["Risk Level"].isin(risk_filter)]
            if country_filter:
                filtered_df = filtered_df[filtered_df["Country"].isin(country_filter)]
            if bin_search:
                filtered_df = filtered_df[filtered_df["BIN"].str.contains(bin_search, na=False)]
            
            # Display data
            st.write(f"### Showing {len(filtered_df)} of {len(bin_df)} BIN Records")
            
            # Columns to display
            default_columns = ["BIN", "Scheme", "Type", "Country", "Issuer", "3DS", "Risk Level"]
            
            # Option to see all columns
            show_all_cols = st.checkbox("Show All Card Details", value=False)
            
            display_df = filtered_df if show_all_cols else filtered_df[default_columns]
            
            # Display with highlighting
            def highlight_3ds(val):
                if val == "Yes ✅":
                    return 'background-color: #d4edda'  # green
                elif val == "No ⚠️":
                    return 'background-color: #fff3cd'  # yellow
                return ''
                
            def highlight_risk(val):
                if val == "Enforced":
                    return 'background-color: #d4edda'  # green
                elif val == "Weak":
                    return 'background-color: #fff3cd'  # yellow
                elif val == "Unsafe":
                    return 'background-color: #f8d7da'  # red
                return ''
            
            # Apply styling
            styled_df = display_df.style.map(highlight_3ds, subset=['3DS'] if '3DS' in display_df.columns else [])
            styled_df = styled_df.map(highlight_risk, subset=['Risk Level'] if 'Risk Level' in display_df.columns else [])
            
            st.dataframe(styled_df)
            
            # Export option
            if st.button("Export to CSV"):
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="bin_records.csv",
                    mime="text/csv"
                )
        else:
            st.info("No BIN records found in the database.")
    except Exception as e:
        st.error(f"Error retrieving database records: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center">
    <p>🔒 BIN Intelligence & 3DS Enforcement Checker | Cybersecurity Research Tool</p>
</div>
""", unsafe_allow_html=True)
