#!/bin/bash
# GitHub & Railway Deployment Setup Script
# Run from: d:\betty\impact

echo "🚀 HCCMS Deployment Setup"
echo "========================="
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git not found. Please install Git first."
    exit 1
fi

echo "✅ Git is installed"
echo ""

# Initialize git repo
if [ ! -d ".git" ]; then
    echo "📝 Initializing git repository..."
    git init
    echo "✅ Git repo initialized"
else
    echo "ℹ️  Git repo already exists"
fi

echo ""
echo "📋 Current git status:"
git status --short | head -10

echo ""
echo "=== NEXT STEPS ==="
echo ""
echo "1. Create a GitHub repository:"
echo "   - Go to https://github.com/new"
echo "   - Name it: victori (or hccms-flask)"
echo "   - Click 'Create repository'"
echo ""

echo "2. Add GitHub remote (replace USERNAME and REPO):"
echo "   git remote add origin https://github.com/USERNAME/REPO.git"
echo ""

echo "3. Commit and push code:"
echo "   git add -A"
echo "   git commit -m 'Initial HCCMS project commit'"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""

echo "4. Deploy to Railway:"
echo "   - Go to https://railway.app"
echo "   - Click 'New Project'"
echo "   - Select 'Deploy from GitHub repo'"
echo "   - Choose your victori repository"
echo "   - Railway auto-deploys!"
echo ""

echo "5. Get your Railway URL and test:"
echo "   curl https://YOUR-RAILWAY-URL/health"
echo ""
