#!/bin/bash

# Sync BIN Intelligence Project to GitHub
# Repository: https://github.com/isndotbiz/bin-intelligence-checker.git

echo "🔒 Syncing BIN Intelligence & 3DS Enforcement Checker to GitHub"
echo "=============================================================="

# Set up remote if not already set
echo "Setting up GitHub remote..."
git remote add origin https://github.com/isndotbiz/bin-intelligence-checker.git 2>/dev/null || echo "Remote already exists"

# Add all project files
echo "Adding files to Git..."
git add README.md
git add CHANGELOG.md
git add LICENSE
git add .gitignore
git add app.py
git add bin_checker.py
git add bin_scraper.py
git add database.py
git add utils.py
git add replit.md
git add .streamlit/config.toml
git add GITHUB_SETUP.md
git add PROJECT_SUMMARY.md

# Create comprehensive commit
echo "Creating commit..."
git commit -m "Initial commit: BIN Intelligence & 3DS Enforcement Checker v1.0.0

✨ Features:
- Complete Streamlit application with BIN analysis
- 3DS enforcement checking and risk assessment
- Web scraping capabilities for BIN discovery
- Dollar threshold tracking system
- Database persistence with SQLite
- Risk classification (Enforced, Weak, Unsafe)
- Data export capabilities

🛠️ Technical:
- RapidAPI 3ds-lookup integration
- SQLAlchemy ORM with database models
- BeautifulSoup web scraping
- Comprehensive input validation
- Professional error handling

📚 Documentation:
- Complete README with installation guide
- CHANGELOG following semantic versioning
- MIT license for open source
- GitHub setup instructions
- Professional project structure

🎨 UI/UX:
- Clean Streamlit interface with emoji icons
- Color-coded risk visualization
- Responsive data tables
- Form validation and error feedback
- Multi-tab organization

Ready for deployment and collaboration!"

# Push to GitHub
echo "Pushing to GitHub..."
git branch -M main
git push -u origin main

echo ""
echo "✅ Successfully synced to GitHub!"
echo "🔗 Repository: https://github.com/isndotbiz/bin-intelligence-checker"
echo ""
echo "Next steps:"
echo "1. Visit your repository to verify all files uploaded"
echo "2. Add repository topics: streamlit, cybersecurity, payment-security"
echo "3. Deploy to Streamlit Cloud: share.streamlit.io"
echo "4. Configure API secrets for deployment"
echo ""
echo "🚀 Project is ready for the world!"