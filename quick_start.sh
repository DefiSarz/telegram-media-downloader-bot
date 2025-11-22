#!/bin/bash

# Quick Start Script for Telegram Media Downloader Bot
# This script automates the setup process

set -e

echo "🎬 Telegram Media Downloader Bot - Quick Start"
echo "=============================================="
echo ""

# Check Python version
echo "📋 Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Python $PYTHON_VERSION found"

# Check FFmpeg
echo ""
echo "📋 Checking FFmpeg..."
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  FFmpeg is not installed."
    echo ""
    echo "Install FFmpeg:"
    echo "  • Ubuntu/Debian: sudo apt install ffmpeg"
    echo "  • macOS: brew install ffmpeg"
    echo "  • Windows: Download from https://ffmpeg.org/download.html"
    echo ""
    read -p "Continue without FFmpeg? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ FFmpeg found"
fi

# Create virtual environment
echo ""
echo "🔧 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "🔌 Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependencies installed"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "⚙️  Creating .env file..."
    cp .env.example .env
    echo "✅ .env file created"
    
    echo ""
    echo "🔑 Please configure your bot:"
    echo ""
    read -p "Enter your Telegram Bot Token: " bot_token
    
    # Update .env file
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/BOT_TOKEN=.*/BOT_TOKEN=$bot_token/" .env
    else
        # Linux
        sed -i "s/BOT_TOKEN=.*/BOT_TOKEN=$bot_token/" .env
    fi
    
    echo "✅ Bot token configured"
else
    echo ""
    echo "✅ .env file already exists"
fi

# Create downloads directory
echo ""
echo "📁 Creating downloads directory..."
mkdir -p downloads
echo "✅ Downloads directory ready"

# Success message
echo ""
echo "=============================================="
echo "🎉 Setup Complete!"
echo "=============================================="
echo ""
echo "📋 Next steps:"
echo ""
echo "1. Verify your bot token in .env file:"
echo "   nano .env"
echo ""
echo "2. Start the bot:"
echo "   source venv/bin/activate  # If not already activated"
echo "   python telegram_media_bot.py"
echo ""
echo "3. Open Telegram and send /start to your bot"
echo ""
echo "📚 For more information, see:"
echo "   • README.md - Overview and features"
echo "   • SETUP_GUIDE.md - Detailed setup instructions"
echo ""
echo "🚀 Happy downloading!"
echo ""

# Ask if user wants to start the bot now
read -p "Would you like to start the bot now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🚀 Starting bot..."
    python telegram_media_bot.py
fi
