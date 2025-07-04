#!/bin/bash

# GitHub Repository Setup Script
# This script helps initialize a Git repository and provides instructions for GitHub sync

echo "🔒 BIN Intelligence & 3DS Enforcement Checker - GitHub Setup"
echo "============================================================"

# Initialize git repository if not already initialized
if [ ! -d ".git" ]; then
    echo "Initializing Git repository..."
    git init
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository already exists"
fi

# Add gitignore and initial files
echo "Adding files to Git..."
git add .gitignore
git add README.md
git add CHANGELOG.md
git add LICENSE
git add replit.md
git add app.py
git add bin_checker.py
git add bin_scraper.py
git add database.py
git add utils.py
git add .streamlit/

# Make initial commit
echo "Making initial commit..."
git commit -m "Initial commit: BIN Intelligence & 3DS Enforcement Checker v1.0.0

- Complete Streamlit application with BIN analysis
- 3DS enforcement checking and risk assessment
- Web scraping capabilities for BIN discovery
- Database persistence with SQLite
- Comprehensive documentation and best practices"

echo ""
echo "🎉 Local Git repository is ready!"
echo ""
echo "Next steps to sync with GitHub:"
echo "1. Create a new repository on GitHub: https://github.com/new"
echo "2. Copy the repository URL (e.g., https://github.com/username/bin-intelligence-checker.git)"
echo "3. Run the following commands:"
echo ""
echo "   git remote add origin YOUR_GITHUB_REPOSITORY_URL"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "Alternative: Use GitHub CLI if installed:"
echo "   gh repo create bin-intelligence-checker --public --push"
echo ""
echo "📋 Repository contains:"
echo "   - Complete application code"
echo "   - Documentation (README.md, CHANGELOG.md)"
echo "   - License (MIT)"
echo "   - Best practices (.gitignore, proper file structure)"
echo "   - Project configuration"
echo ""
echo "🚀 Ready for deployment and collaboration!"