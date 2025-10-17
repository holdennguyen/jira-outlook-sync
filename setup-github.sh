#!/bin/bash

# GitHub Repository Setup Script for jira-outlook-sync

echo "🚀 Setting up GitHub repository for jira-outlook-sync"
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed."
    echo "   Install it from: https://cli.github.com/"
    echo ""
    echo "   Or use Homebrew: brew install gh"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ Not authenticated with GitHub CLI"
    echo "   Run: gh auth login"
    exit 1
fi

echo "✅ GitHub CLI is installed and authenticated"
echo ""

# Confirm repository creation
echo "This will create a new GitHub repository:"
echo "  Name: jira-outlook-sync"
echo "  Description: Automatically sync Jira ticket planned dates to Outlook calendar events"
echo "  Visibility: Public (you can change this)"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

# Create the repository on GitHub
echo "📦 Creating GitHub repository..."
gh repo create jira-outlook-sync \
    --public \
    --description "Automatically sync Jira ticket planned dates to Outlook calendar events" \
    --source=. \
    --remote=origin \
    --push

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Repository created successfully!"
    echo ""
    echo "🔗 Repository URL: https://github.com/$(gh api user -q .login)/jira-outlook-sync"
    echo ""
    echo "📋 Next steps:"
    echo "  1. Visit the repository and configure settings"
    echo "  2. Add repository secrets for CI/CD (if needed)"
    echo "  3. Enable GitHub Actions if you plan to use scheduled syncs"
    echo "  4. Start implementing the proposal tasks!"
    echo ""
else
    echo ""
    echo "❌ Failed to create repository"
    echo ""
    echo "Manual steps:"
    echo "  1. Go to https://github.com/new"
    echo "  2. Create a repository named 'jira-outlook-sync'"
    echo "  3. Run these commands:"
    echo ""
    echo "     git remote add origin git@github.com:YOUR_USERNAME/jira-outlook-sync.git"
    echo "     git push -u origin main"
    echo ""
fi
