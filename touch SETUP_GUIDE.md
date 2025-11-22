# Telegram Media Downloader Bot - Setup Guide

## 🎯 Overview

This bot downloads videos and audio from YouTube, Newgrounds, Instagram, TikTok, Twitter, Facebook, Reddit, and 1500+ other sites supported by yt-dlp.

## ✨ Features

- **Multi-platform support**: YouTube, Newgrounds, Instagram, TikTok, Twitter/X, Facebook, Reddit, Vimeo, and more
- **Quality selection**: Choose from Best, 1080p, 720p, or 480p
- **Audio extraction**: Download audio-only in MP3 format (320kbps)
- **Progress tracking**: Real-time download progress updates
- **Group chat support**: Works in both private and group chats
- **User whitelist**: Optional user authorization
- **Automatic cleanup**: Downloaded files are removed after upload

## 📋 Prerequisites

1. **Python 3.8+**
2. **FFmpeg** (required for audio conversion and video processing)
3. **Telegram Bot Token** from [@BotFather](https://t.me/BotFather)

## 🔧 Installation

### Step 1: Install Python Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

### Step 2: Install FFmpeg

**Windows:**
1. Download from: https://ffmpeg.org/download.html
2. Extract to a folder (e.g., `C:\ffmpeg`)
3. Add to PATH: `C:\ffmpeg\bin`

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

### Step 3: Create Your Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` command
3. Choose a name for your bot (e.g., "My Media Downloader")
4. Choose a username (must end in 'bot', e.g., "my_media_dl_bot")
5. Copy the bot token (looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Step 4: Configure the Bot

**Option A: Environment Variables (Recommended)**

```bash
# Linux/macOS
export BOT_TOKEN="your_bot_token_here"
export DOWNLOAD_PATH="./downloads"
export MAX_FILE_SIZE_MB="50"
export ALLOWED_USERS=""  # Optional: comma-separated user IDs

# Windows (PowerShell)
$env:BOT_TOKEN="your_bot_token_here"
$env:DOWNLOAD_PATH="./downloads"
$env:MAX_FILE_SIZE_MB="50"
```

**Option B: Edit the Code**

Open `telegram_media_bot.py` and change:
```python
BOT_TOKEN = 'YOUR_ACTUAL_BOT_TOKEN_HERE'
```

### Step 5: Run the Bot

```bash
python telegram_media_bot.py
```

You should see:
```
🚀 Bot started successfully!
🤖 Bot is running... Press Ctrl+C to stop
```

## 🎮 Usage

### Basic Commands

- `/start` - Welcome message and bot info
- `/help` - Detailed help and instructions
- `/quality` - Select video quality (Best, 1080p, 720p, 480p)
- `/audio` - Switch to audio-only mode (MP3)
- `/video` - Switch to video mode (default)

### Downloading Media

1. Simply send any URL to the bot
2. The bot will automatically detect and download the media
3. You'll receive progress updates
4. Media will be uploaded directly to Telegram

### Examples

**Download YouTube video:**
```
https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

**Download Newgrounds animation:**
```
https://www.newgrounds.com/portal/view/854273
```

**Download Instagram Reel:**
```
https://www.instagram.com/p/CXpxSyOrWCA/
```

**Download TikTok video:**
```
https://www.tiktok.com/@user/video/1234567890
```

## 🔐 Optional: User Whitelist

To restrict bot access to specific users:

1. Get your Telegram user ID:
   - Message [@userinfobot](https://t.me/userinfobot)
   - It will reply with your user ID

2. Set the whitelist:
   ```bash
   export ALLOWED_USERS="123456789,987654321"  # Comma-separated user IDs
   ```

## 🐳 Docker Deployment (Optional)

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

# Install FFmpeg
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY telegram_media_bot.py .

CMD ["python", "telegram_media_bot.py"]
```

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  bot:
    build: .
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
      - DOWNLOAD_PATH=/downloads
      - MAX_FILE_SIZE_MB=50
      - ALLOWED_USERS=${ALLOWED_USERS}
    volumes:
      - ./downloads:/downloads
    restart: unless-stopped
```

Run with:
```bash
docker-compose up -d
```

## 📊 Supported Sites

The bot supports **1500+ websites** including:

### Video Platforms
- YouTube (videos, shorts, playlists)
- Vimeo
- Dailymotion
- Twitch
- Newgrounds ✨

### Social Media
- Instagram (posts, reels, stories, IGTV)
- TikTok
- Twitter/X
- Facebook
- Reddit
- Pinterest
- LinkedIn
- Snapchat

### And Many More!
Full list: https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md

## ⚠️ Limitations

1. **File Size**: Telegram limits non-premium uploads to 50MB (2GB for premium)
2. **Rate Limits**: Some sites may rate-limit requests
3. **Private Content**: Cannot download private/restricted videos without authentication
4. **Age-Restricted**: Some content may require cookies for age verification
5. **DRM Content**: Cannot download DRM-protected content

## 🔍 Troubleshooting

### "HTTP Error 403" or "Unable to download"
- Site may require authentication/cookies
- Video might be geo-restricted
- Try updating yt-dlp: `pip install -U yt-dlp`

### "File too large"
- Select a lower quality: `/quality` → Choose 720p or 480p
- Or use audio-only mode: `/audio`

### FFmpeg not found
- Make sure FFmpeg is installed and in your PATH
- Test: `ffmpeg -version`

### Newgrounds videos not downloading
- Some Newgrounds content requires login
- Update yt-dlp to latest version
- Check if video is publicly accessible

### Bot doesn't respond
- Verify bot token is correct
- Check bot is running without errors
- Ensure you've sent `/start` first

## 🚀 Advanced Configuration

### Custom yt-dlp Options

Edit the `get_yt_dlp_options` method to add custom options:

```python
base_opts = {
    'outtmpl': output_template,
    'quiet': False,
    # Add custom options here:
    'extract_flat': False,
    'age_limit': 18,  # Skip videos with age restriction
    'playlist_items': '1-10',  # Download first 10 items of playlist
}
```

### Using Cookies for Private Content

For age-restricted or private content:

1. Export cookies from your browser:
   - Chrome: Use "Get cookies.txt LOCALLY" extension
   - Firefox: Use "cookies.txt" extension

2. Save cookies to `cookies.txt`

3. Update yt-dlp options:
   ```python
   base_opts['cookiefile'] = 'cookies.txt'
   ```

### Playlist Support

The bot already supports playlists! Just send a playlist URL:
```
https://www.youtube.com/playlist?list=PLXXXXXX
```

### Enable Download History

Track download history in SQLite:

```python
# Add at top of file
import sqlite3

# Initialize database
conn = sqlite3.connect('downloads.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS downloads
    (id INTEGER PRIMARY KEY, user_id TEXT, url TEXT, timestamp TEXT)
''')
conn.commit()
```

## 📝 License & Legal

**Important Legal Notice:**
- This bot is for educational purposes only
- Respect copyright laws and terms of service
- Only download content you have rights to
- Some platforms prohibit automated downloads
- Use responsibly and at your own risk

**Recommended Use:**
- Creative Commons licensed content
- Personal backups of your own content
- Educational and research purposes
- Content with explicit download permission

## 🤝 Contributing

Found a bug or want to add features? Feel free to:
- Report issues
- Submit pull requests
- Suggest improvements

## 📚 Resources

- [yt-dlp Documentation](https://github.com/yt-dlp/yt-dlp)
- [python-telegram-bot Documentation](https://docs.python-telegram-bot.org/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [FFmpeg Documentation](https://ffmpeg.org/documentation.html)

## 💡 Tips

1. **Premium Telegram**: Upgrade to Telegram Premium for 4GB file size limit
2. **VPS Hosting**: Deploy on a VPS for 24/7 availability
3. **Rate Limiting**: Implement rate limiting to prevent abuse
4. **Monitoring**: Use logging to track usage and errors
5. **Updates**: Regularly update yt-dlp for latest site support

## 🎉 Enjoy!

Your bot is now ready to download media from YouTube, Newgrounds, and 1500+ other sites!

For questions or issues, check the troubleshooting section or review the yt-dlp documentation.
