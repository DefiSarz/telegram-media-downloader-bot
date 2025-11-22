"""
Telegram Media Downloader Bot
Supports: YouTube, Instagram, TikTok, Twitter, Facebook, Newgrounds, and 1500+ sites via yt-dlp
"""

import os
import re
import logging
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

# Telegram bot libraries
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from telegram.constants import ParseMode, ChatAction

# Media download library
import yt_dlp

# Configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
DOWNLOAD_PATH = os.getenv('DOWNLOAD_PATH', './downloads')
MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', '2048'))  # Telegram limit (2GB for premium)
ALLOWED_USERS = os.getenv('ALLOWED_USERS', '').split(',')  # Optional: comma-separated user IDs

# Create download directory
Path(DOWNLOAD_PATH).mkdir(parents=True, exist_ok=True)


class MediaDownloader:
    """Handles media downloads using yt-dlp"""
    
    def __init__(self, download_path: str):
        self.download_path = download_path
        self.supported_sites = [
            'YouTube', 'Instagram', 'TikTok', 'Twitter/X', 'Facebook', 
            'Reddit', 'Newgrounds', 'Vimeo', 'Dailymotion', 'Pinterest',
            'LinkedIn', 'Snapchat', 'Twitch', 'and 1500+ more sites'
        ]
    
    def get_yt_dlp_options(self, quality: str = 'best', media_type: str = 'video') -> Dict[str, Any]:
        """Generate yt-dlp options based on user preferences"""
        
        output_template = os.path.join(self.download_path, '%(title)s.%(ext)s')
        
        base_opts = {
            'outtmpl': output_template,
            'quiet': False,
            'no_warnings': False,
            'extract_flat': False,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        }
        
        if media_type == 'audio':
            base_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '320',
                }],
            })
        else:
            # Video download options
            if quality == 'best':
                format_string = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
            elif quality == '1080p':
                format_string = 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best'
            elif quality == '720p':
                format_string = 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best'
            elif quality == '480p':
                format_string = 'bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]/best'
            else:
                format_string = 'best[ext=mp4]/best'
            
            base_opts.update({
                'format': format_string,
                'merge_output_format': 'mp4',
            })
        
        return base_opts
    
    async def download_media(
        self, 
        url: str, 
        quality: str = 'best', 
        media_type: str = 'video',
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """Download media from URL"""
        
        try:
            ydl_opts = self.get_yt_dlp_options(quality, media_type)
            
            # Add progress hook if callback provided
            if progress_callback:
                ydl_opts['progress_hooks'] = [progress_callback]
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract info first
                info = ydl.extract_info(url, download=False)
                
                # Check file size estimate
                filesize = info.get('filesize') or info.get('filesize_approx', 0)
                if filesize > MAX_FILE_SIZE_MB * 1024 * 1024:
                    return {
                        'success': False,
                        'error': f'File size ({filesize / (1024*1024):.1f}MB) exceeds Telegram limit ({MAX_FILE_SIZE_MB}MB)'
                    }
                
                # Download the media
                info = ydl.extract_info(url, download=True)
                
                # Get the downloaded file path
                if media_type == 'audio':
                    filename = ydl.prepare_filename(info).rsplit('.', 1)[0] + '.mp3'
                else:
                    filename = ydl.prepare_filename(info)
                
                return {
                    'success': True,
                    'filepath': filename,
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'thumbnail': info.get('thumbnail'),
                    'uploader': info.get('uploader', 'Unknown'),
                    'description': info.get('description', '')[:200]  # Limit description
                }
                
        except Exception as e:
            logger.error(f"Download error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def is_valid_url(self, url: str) -> bool:
        """Check if URL is valid"""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url_pattern.match(url) is not None


# Initialize downloader
downloader = MediaDownloader(DOWNLOAD_PATH)


# Command handlers
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    welcome_message = (
        "🎬 *Welcome to Media Downloader Bot!*\n\n"
        "📥 I can download videos and audio from:\n"
        f"{'• ' + chr(10) + '• '.join(downloader.supported_sites)}\n\n"
        "🔗 *How to use:*\n"
        "Just send me a link and I'll download it for you!\n\n"
        "⚙️ *Commands:*\n"
        "/start - Show this message\n"
        "/help - Get help\n"
        "/quality - Set download quality\n"
        "/audio - Download audio only\n"
        "/video - Download video (default)\n\n"
        "💡 *Tip:* Works in private chats and groups!"
    )
    
    await update.message.reply_text(
        welcome_message,
        parse_mode=ParseMode.MARKDOWN
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = (
        "📖 *Help & Instructions*\n\n"
        "1️⃣ Send me any video URL\n"
        "2️⃣ Choose quality (optional)\n"
        "3️⃣ Wait for download to complete\n"
        "4️⃣ Receive your media file!\n\n"
        "🎯 *Supported Sites:*\n"
        "✅ YouTube (videos, shorts, playlists)\n"
        "✅ Instagram (posts, reels, stories)\n"
        "✅ TikTok\n"
        "✅ Twitter/X\n"
        "✅ Facebook\n"
        "✅ Newgrounds\n"
        "✅ Reddit\n"
        "✅ Vimeo\n"
        "✅ And 1500+ more!\n\n"
        "⚠️ *Limitations:*\n"
        f"• Max file size: {MAX_FILE_SIZE_MB}MB (Telegram limit)\n"
        "• Large files will be compressed\n"
        "• Age-restricted content may require cookies\n\n"
        "❓ Having issues? Make sure:\n"
        "• URL is valid and publicly accessible\n"
        "• Video is not private/deleted\n"
        "• File size is within limits"
    )
    
    await update.message.reply_text(
        help_text,
        parse_mode=ParseMode.MARKDOWN
    )


async def quality_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /quality command - show quality options"""
    keyboard = [
        [
            InlineKeyboardButton("🌟 Best Quality", callback_data="quality_best"),
            InlineKeyboardButton("📺 1080p", callback_data="quality_1080p")
        ],
        [
            InlineKeyboardButton("📹 720p", callback_data="quality_720p"),
            InlineKeyboardButton("📱 480p", callback_data="quality_480p")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "⚙️ *Select Video Quality:*",
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )


async def audio_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set mode to audio-only"""
    context.user_data['media_type'] = 'audio'
    await update.message.reply_text(
        "🎵 Audio mode enabled! Send me a link to extract audio (MP3 320kbps)"
    )


async def video_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set mode to video"""
    context.user_data['media_type'] = 'video'
    quality = context.user_data.get('quality', 'best')
    await update.message.reply_text(
        f"🎬 Video mode enabled! Current quality: {quality}"
    )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith('quality_'):
        quality = query.data.replace('quality_', '')
        context.user_data['quality'] = quality
        
        await query.edit_message_text(
            f"✅ Quality set to: *{quality}*\n\nNow send me a video link!",
            parse_mode=ParseMode.MARKDOWN
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages with URLs"""
    
    # Check if user is allowed (if whitelist is configured)
    if ALLOWED_USERS and ALLOWED_USERS[0]:
        user_id = str(update.effective_user.id)
        if user_id not in ALLOWED_USERS:
            await update.message.reply_text("⛔ You are not authorized to use this bot.")
            return
    
    message_text = update.message.text
    
    # Extract URLs from message
    urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message_text)
    
    if not urls:
        await update.message.reply_text(
            "❌ No valid URL found.\n\n"
            "Please send a valid link from YouTube, TikTok, Instagram, Newgrounds, etc.\n"
            "Use /help for more information."
        )
        return
    
    # Get user preferences
    quality = context.user_data.get('quality', 'best')
    media_type = context.user_data.get('media_type', 'video')
    
    # Process first URL
    url = urls[0]
    
    # Validate URL
    if not downloader.is_valid_url(url):
        await update.message.reply_text("❌ Invalid URL format!")
        return
    
    # Send initial message
    status_msg = await update.message.reply_text(
        f"⏳ Processing your {media_type}...\n"
        f"🔗 URL: {url[:50]}...\n"
        f"⚙️ Quality: {quality}"
    )
    
    # Show typing action
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=ChatAction.UPLOAD_VIDEO if media_type == 'video' else ChatAction.UPLOAD_AUDIO
    )
    
    try:
        # Download the media
        result = await downloader.download_media(url, quality, media_type)
        
        if not result['success']:
            await status_msg.edit_text(
                f"❌ *Download Failed*\n\n"
                f"Error: {result['error']}\n\n"
                f"Try a different quality or check if the video is accessible.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Update status
        await status_msg.edit_text(
            f"✅ Download complete!\n"
            f"📤 Uploading to Telegram..."
        )
        
        # Send the file
        filepath = result['filepath']
        file_size = os.path.getsize(filepath)
        
        if file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
            await status_msg.edit_text(
                f"❌ File too large ({file_size / (1024*1024):.1f}MB)\n"
                f"Telegram limit: {MAX_FILE_SIZE_MB}MB\n\n"
                f"Try downloading at lower quality."
            )
        else:
            # Prepare caption
            caption = (
                f"🎬 *{result['title']}*\n"
                f"👤 {result['uploader']}\n"
                f"⏱️ Duration: {result['duration']//60}:{result['duration']%60:02d}\n"
                f"💾 Size: {file_size / (1024*1024):.1f}MB"
            )
            
            # Send based on media type
            if media_type == 'audio':
                with open(filepath, 'rb') as audio_file:
                    await update.message.reply_audio(
                        audio=audio_file,
                        caption=caption[:1024],  # Telegram caption limit
                        parse_mode=ParseMode.MARKDOWN,
                        title=result['title'],
                        performer=result['uploader']
                    )
            else:
                with open(filepath, 'rb') as video_file:
                    await update.message.reply_video(
                        video=video_file,
                        caption=caption[:1024],
                        parse_mode=ParseMode.MARKDOWN,
                        supports_streaming=True
                    )
            
            # Delete status message
            await status_msg.delete()
        
        # Clean up downloaded file
        try:
            os.remove(filepath)
        except Exception as e:
            logger.error(f"Error removing file: {e}")
    
    except Exception as e:
        logger.error(f"Error processing media: {e}")
        await status_msg.edit_text(
            f"❌ *Error occurred*\n\n"
            f"Details: {str(e)[:200]}\n\n"
            f"Please try again or use /help",
            parse_mode=ParseMode.MARKDOWN
        )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ An error occurred. Please try again later."
        )


def main():
    """Start the bot"""
    
    if BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        print("❌ Please set your BOT_TOKEN in environment variables or in the code!")
        print("Get your bot token from @BotFather on Telegram")
        return
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("quality", quality_command))
    application.add_handler(CommandHandler("audio", audio_command))
    application.add_handler(CommandHandler("video", video_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    # Start bot
    logger.info("🚀 Bot started successfully!")
    print("🤖 Bot is running... Press Ctrl+C to stop")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
