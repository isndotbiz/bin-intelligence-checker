# BIN Intelligence & 3DS Enforcement Checker

A comprehensive Streamlit web application for analyzing Bank Identification Numbers (BINs) and 3D Secure (3DS) enforcement to identify payment security risks and fraud patterns.

## Features

### 🔒 BIN & Card Analysis
- Analyze 6-digit BINs or full card numbers for 3DS enforcement
- Validate card schemes (Visa, Mastercard, etc.)
- Check issuer information and country of origin
- Optional IP geolocation context

### 🔍 Web Scraping Intelligence
- Extract potential BIN numbers from websites
- Automatic fraud context detection
- Batch analysis of discovered BINs
- Risk assessment based on source context

### 💰 Threshold Tracking
- Test 3DS triggers at specific dollar amounts
- Track threshold patterns across different BINs
- Historical threshold analysis

### 📊 Database History
- Persistent storage of all analysis results
- Comprehensive search and filtering
- Data export capabilities (CSV)
- Risk-based visualization with color coding

## Risk Classification System

- **✅ Enforced**: 3DS authentication is active
- **⚠️ Weak**: 3DS authentication is missing or inconsistent
- **❌ Unsafe**: Found in fraud context with no 3DS protection

## Installation

### Prerequisites
- Python 3.8+
- RapidAPI account with 3ds-lookup API access

### Setup
1. Clone the repository:
```bash
git clone <repository-url>
cd bin-intelligence-checker
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your API key:
   - Get your RapidAPI key from [3ds-lookup API](https://rapidapi.com/3ds-lookup/api/3ds-lookup)
   - The application will prompt for the API key on first use

4. Run the application:
```bash
streamlit run app.py --server.port 5000
```

## Usage

### Basic BIN Checking
1. Navigate to the "BIN Checker" tab
2. Enter a 6-digit BIN (e.g., `411111`) or full card number
3. Optionally provide an IP address for geolocation context
4. Click "Check BIN" to analyze

### Web Scraping
1. Go to the "URL Scraper" tab
2. Enter a URL to scan for BIN numbers
3. The tool will automatically extract and analyze found BINs
4. Results include fraud context assessment

### Threshold Testing
1. Use the "Threshold Tracker" tab
2. Enter a BIN and dollar amount
3. Test whether 3DS is triggered at that threshold
4. View historical threshold data

### Database Management
1. Access the "Database History" tab
2. View all stored analysis results
3. Filter by risk level or search specific BINs
4. Export data as CSV for further analysis

## Technical Architecture

### Backend
- **Framework**: Streamlit
- **Database**: SQLite with SQLAlchemy ORM
- **API Integration**: RapidAPI 3ds-lookup service
- **Web Scraping**: BeautifulSoup4 + Trafilatura

### Database Schema
- `bin_records`: Stores BIN analysis results with metadata
- `threshold_records`: Tracks dollar threshold testing results

### Key Components
- `app.py`: Main Streamlit application
- `bin_checker.py`: BIN analysis and API integration
- `bin_scraper.py`: Web scraping functionality
- `database.py`: Database models and operations
- `utils.py`: Validation and utility functions

## API Reference

### 3ds-lookup API
- **Endpoint**: `https://3ds-lookup.p.rapidapi.com/cards/`
- **Method**: POST
- **Parameters**:
  - `card_number`: 6-digit BIN or full card number
  - `ip_address`: Optional IP for geolocation

## Configuration

### Streamlit Configuration
The application uses custom configuration in `.streamlit/config.toml`:
```toml
[server]
headless = true
address = "0.0.0.0"
port = 5000
```

## Security Considerations

- API keys are handled securely through environment variables
- No sensitive card data is stored permanently
- All database operations use parameterized queries
- Input validation prevents injection attacks

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is designed for cybersecurity research and educational purposes. Users are responsible for ensuring compliance with applicable laws and regulations when analyzing payment card data.

## Support

For issues, questions, or feature requests, please open an issue on GitHub.