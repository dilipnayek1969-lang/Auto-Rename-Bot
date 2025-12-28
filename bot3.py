#!/usr/bin/env python3
"""
Auto Rename Bot - Render Deployment Version
Optimized for Render hosting
"""

import os
import re
import sys
import time
import json
import math
import asyncio
import logging
import datetime
import shutil
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dotenv import load_dotenv
from PIL import Image
import motor.motor_asyncio
from pyrogram import Client, filters, __version__
from pyrogram.types import (
    Message, InlineKeyboardButton, InlineKeyboardMarkup, 
    CallbackQuery
)
from pyrogram.errors import (
    FloodWait, InputUserDeactivated, UserIsBlocked, 
    PeerIdInvalid
)

# Load environment variables
load_dotenv()

# ==================== CONFIGURATION ====================
class Config:
    API_ID = int(os.getenv("API_ID", ""))
    API_HASH = os.getenv("API_HASH", "")
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")
    ADMIN = [int(admin) for admin in os.getenv("ADMIN", "").split(",") if admin.strip()]
    DB_URL = os.getenv("DB_URL", "")
    DB_NAME = os.getenv("DB_NAME", "Filex")
    LOG_CHANNEL = int(os.getenv("LOG_CHANNEL", "0"))
    START_PIC = os.getenv("START_PIC", "https://graph.org/file/29a3acbbab9de5f45a5fe.jpg")
    WEBHOOK = os.getenv("WEBHOOK", "False").lower() == "true"
    PORT = int(os.getenv("PORT", "8080"))
    BOT_UPTIME = time.time()
    # Render specific
    RENDER = os.getenv("RENDER", "false").lower() == "true"
    RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL", "")

class Txt:
    START_TXT = """<b>ʜᴇʏ! {}  

» ɪ ᴀᴍ ᴀᴅᴠᴀɴᴄᴇᴅ ʀᴇɴᴀᴍᴇ ʙᴏᴛ! ᴡʜɪᴄʜ ᴄᴀɴ ᴀᴜᴛᴏʀᴇɴᴀᴍᴇ ʏᴏᴜʀ ғɪʟᴇs ᴡɪᴛʜ ᴄᴜsᴛᴏᴍ ᴄᴀᴘᴛɪᴏɴ ᴀɴᴅ ᴛʜᴜᴍʙɴᴀɪʟ ᴀɴᴅ ᴀʟsᴏ sᴇǫᴜᴇɴᴄᴇ ᴛʜᴇᴍ ᴘᴇʀғᴇᴄᴛʟʏ</b>"""
    
    FILE_NAME_TXT = """<b>» <u>sᴇᴛᴜᴘ ᴀᴜᴛᴏ ʀᴇɴᴀᴍᴇ ғᴏʀᴍᴀᴛ</u></b>

<b>ᴠᴀʀɪᴀʙʟᴇs :</b>
➲ ᴇᴘɪsᴏᴅᴇ - ᴛᴏ ʀᴇᴘʟᴀᴄᴇ ᴇᴘɪsᴏᴅᴇ ɴᴜᴍʙᴇʀ  
➲ sᴇᴀsᴏɴ - ᴛᴏ ʀᴇᴘʟᴀᴄᴇ sᴇᴀsᴏɴ ɴᴜᴍʙᴇʀ  
➲ ǫᴜᴀʟɪᴛʏ - ᴛᴏ ʀᴇᴘʟᴀᴄᴇ ǫᴜᴀʟɪᴛʏ  

<b>‣ ꜰᴏʀ ᴇx:- </b> `/autorename Oᴠᴇʀғʟᴏᴡ [Sseason Eepisode] - [Dual] quality`

<b>‣ /Autorename: ʀᴇɴᴀᴍᴇ ʏᴏᴜʀ ᴍᴇᴅɪᴀ ꜰɪʟᴇs ʙʏ ɪɴᴄʟᴜᴅɪɴɢ 'ᴇᴘɪsᴏᴅᴇ' ᴀɴᴅ 'ǫᴜᴀʟɪᴛʏ' ᴠᴀʀɪᴀʙʟᴇs ɪɴ ʏᴏᴜʀ ᴛᴇxᴛ, ᴛᴏ ᴇxᴛʀᴀᴄᴛ ᴇᴘɪsᴏᴅᴇ ᴀɴᴅ ǫᴜᴀʟɪᴛʏ ᴘʀᴇsᴇɴᴛ ɪɴ ᴛʜᴇ ᴏʀɪɢɪɴᴀʟ ꜰɪʟᴇɴᴀᴍᴇ.</b>"""
    
    CAPTION_TXT = """<b><u>» ᴛᴏ sᴇᴛ ᴄᴜsᴛᴏᴍ ᴄᴀᴘᴛɪᴏɴ ᴀɴᴅ ᴍᴇᴅɪᴀ ᴛʜʏᴘᴇ</u></b>
    
<b>ᴠᴀʀɪᴀʙʟᴇs :</b>         
sɪᴢᴇ: {filesize}
ᴅᴜʀᴀᴛɪᴏɴ: {duration}
ꜰɪʟᴇɴᴀᴍᴇ: {filename}

➲ /set_caption: ᴛᴏ sᴇᴛ ᴀ ᴄᴜsᴛᴏᴍ ᴄᴀᴘᴛɪᴏɴ.
➲ /see_caption: ᴛᴏ ᴠɪᴇᴡ ʏᴏᴜʀ ᴄᴜsᴛᴏᴍ ᴄᴀᴘᴛɪᴏɴ.
➲ /del_caption: ᴛᴏ ᴅᴇʟᴇᴛᴇ ʏᴏᴜʀ ᴄᴜsᴛᴏᴍ ᴄᴀᴘᴛɪᴏɴ.

» ꜰᴏʀ ᴇx:- /set_caption ꜰɪʟᴇ ɴᴀᴍᴇ: {filename}"""

    THUMBNAIL_TXT = """<b><u>» ᴛᴏ sᴇᴛ ᴄᴜsᴛᴏᴍ ᴛʜᴜᴍʙɴᴀɪʟ</u></b>
    
➲ /start: sᴇɴᴅ ᴀɴʏ ᴘʜᴏᴛᴏ ᴛᴏ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ sᴇᴛ ɪᴛ ᴀs ᴀ ᴛʜᴜᴍʙɴᴀɪʟ..
➲ /del_thumb: ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ ᴅᴇʟᴇᴛᴇ ʏᴏᴜʀ ᴏʟᴅ ᴛʜᴜᴍʙɴᴀɪʟ.
➲ /view_thumb: ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ ᴠɪᴇᴡ ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ ᴛʜᴜᴍʙɴᴀɪʟ.

ɴᴏᴛᴇ: ɪꜰ ɴᴏ ᴛʜᴜᴍʙɴᴀɪʟ sᴀᴠᴇᴅ ɪɴ ʙᴏᴛ ᴛʜᴇɴ, ɪᴛ ᴡɪʟʟ ᴜsᴇ ᴛʜᴜᴍʙɴᴀɪʟ ᴏꜰ ᴛʜᴇ ᴏʀɪɢɪɴɪᴀʟ ꜰɪʟᴇ ᴛᴏ sᴇᴛ ɪɴ ʀᴇɴᴀᴍᴇᴅ ꜰɪʟᴇ"""

    PROGRESS_BAR = """\n
<b>» Size</b> : {1} | {2}
<b>» Done</b> : {0}%
<b>» Speed</b> : {3}/s
<b>» ETA</b> : {4} """

    HELP_TXT = """<b>ʜᴇʀᴇ ɪs ʜᴇʟᴘ ᴍᴇɴᴜ ɪᴍᴘᴏʀᴛᴀɴᴛ ᴄᴏᴍᴍᴀɴᴅs:

ᴀᴡᴇsᴏᴍᴇ ғᴇᴀᴛᴜʀᴇs🫧

ʀᴇɴᴀᴍᴇ ʙᴏᴛ ɪs ᴀ ʜᴀɴᴅʏ ᴛᴏᴏʟ ᴛʜᴀᴛ ʜᴇʟᴘs ʏᴏᴜ ʀᴇɴᴀᴍᴇ ᴀɴᴅ ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ꜰɪʟᴇs ᴇꜰꜰᴏʀᴛʟᴇssʟʏ.

➲ /autorename: ᴀᴜᴛᴏ ʀᴇɴᴀᴍᴇ ʏᴏᴜʀ ꜰɪʟᴇs.
➲ /metadata: ᴄᴏᴍᴍᴀɴᴅs ᴛᴏ ᴛᴜʀɴ ᴏɴ/ᴏꜰꜰ ᴍᴇᴛᴀᴅᴀᴛᴀ.
➲ /help: ɢᴇᴛ ǫᴜɪᴄᴋ ᴀssɪsᴛᴀɴᴄᴇ.</b>"""
    
    META_TXT = """<b><u>» How to Set Metadata</u></b>

<b>Available metadata commands:</b>
➲ /settitle - Set the title metadata
➲ /setauthor - Set the author metadata
➲ /setartist - Set the artist metadata  
➲ /setaudio - Set the audio track title
➲ /setsubtitle - Set the subtitle track title
➲ /setvideo - Set the video track title

<b>Example:</b>
<code>/settitle Encoded by @Codeflix_Bots</code>
<code>/setauthor @Codeflix_Bots</code>

<b>Note:</b> Metadata addition does NOT re-encode or reduce quality. It only adds metadata tags."""

# ==================== DATABASE ====================
class Database:
    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(Config.DB_URL)
        self.db = self.client[Config.DB_NAME]
        self.col = self.db.users
    
    def new_user(self, user_id):
        return {
            "_id": int(user_id),
            "join_date": datetime.now().isoformat(),
            "file_id": None,
            "caption": None,
            "metadata": True,
            "title": "Encoded by @Codeflix_Bots",
            "author": "@Codeflix_Bots",
            "artist": "@Codeflix_Bots",
            "audio": "By @Codeflix_Bots",
            "subtitle": "By @Codeflix_Bots",
            "video": "Encoded By @Codeflix_Bots",
            "format_template": None,
            "media_type": "document",
            "ban_status": {
                "is_banned": False,
                "ban_duration": 0,
                "banned_on": datetime.max.isoformat(),
                "ban_reason": ''
            }
        }
    
    async def add_user(self, user_id):
        if not await self.is_user_exist(user_id):
            user = self.new_user(user_id)
            await self.col.insert_one(user)
    
    async def is_user_exist(self, user_id):
        user = await self.col.find_one({"_id": int(user_id)})
        return bool(user)
    
    async def total_users_count(self):
        return await self.col.count_documents({})
    
    async def get_all_users(self):
        return self.col.find({})
    
    async def delete_user(self, user_id):
        await self.col.delete_many({"_id": int(user_id)})
    
    async def set_thumbnail(self, user_id, file_id):
        await self.col.update_one({"_id": int(user_id)}, {"$set": {"file_id": file_id}})
    
    async def get_thumbnail(self, user_id):
        user = await self.col.find_one({"_id": int(user_id)})
        return user.get("file_id", None) if user else None
    
    async def set_caption(self, user_id, caption):
        await self.col.update_one({"_id": int(user_id)}, {"$set": {"caption": caption}})
    
    async def get_caption(self, user_id):
        user = await self.col.find_one({"_id": int(user_id)})
        return user.get("caption", None) if user else None
    
    async def set_format_template(self, user_id, format_template):
        await self.col.update_one({"_id": int(user_id)}, {"$set": {"format_template": format_template}})
    
    async def get_format_template(self, user_id):
        user = await self.col.find_one({"_id": int(user_id)})
        return user.get("format_template", None) if user else None
    
    async def set_media_preference(self, user_id, media_type):
        await self.col.update_one({"_id": int(user_id)}, {"$set": {"media_type": media_type}})
    
    async def get_media_preference(self, user_id):
        user = await self.col.find_one({"_id": int(user_id)})
        return user.get("media_type", "document") if user else "document"
    
    async def get_metadata(self, user_id):
        user = await self.col.find_one({"_id": int(user_id)})
        return user.get("metadata", True) if user else True
    
    async def set_metadata(self, user_id, metadata):
        if isinstance(metadata, str):
            metadata = metadata.lower() == "on"
        await self.col.update_one({"_id": int(user_id)}, {"$set": {"metadata": metadata}})
    
    async def get_title(self, user_id):
        user = await self.col.find_one({"_id": int(user_id)})
        return user.get("title", "Encoded by @Codeflix_Bots") if user else "Encoded by @Codeflix_Bots"
    
    async def set_title(self, user_id, title):
        await self.col.update_one({"_id": int(user_id)}, {"$set": {"title": title}})
    
    async def get_author(self, user_id):
        user = await self.col.find_one({"_id": int(user_id)})
        return user.get("author", "@Codeflix_Bots") if user else "@Codeflix_Bots"
    
    async def set_author(self, user_id, author):
        await self.col.update_one({"_id": int(user_id)}, {"$set": {"author": author}})
    
    async def get_artist(self, user_id):
        user = await self.col.find_one({"_id": int(user_id)})
        return user.get("artist", "@Codeflix_Bots") if user else "@Codeflix_Bots"
    
    async def set_artist(self, user_id, artist):
        await self.col.update_one({"_id": int(user_id)}, {"$set": {"artist": artist}})
    
    async def get_audio(self, user_id):
        user = await self.col.find_one({"_id": int(user_id)})
        return user.get("audio", "By @Codeflix_Bots") if user else "By @Codeflix_Bots"
    
    async def set_audio(self, user_id, audio):
        await self.col.update_one({"_id": int(user_id)}, {"$set": {"audio": audio}})
    
    async def get_subtitle(self, user_id):
        user = await self.col.find_one({"_id": int(user_id)})
        return user.get("subtitle", "By @Codeflix_Bots") if user else "By @Codeflix_Bots"
    
    async def set_subtitle(self, user_id, subtitle):
        await self.col.update_one({"_id": int(user_id)}, {"$set": {"subtitle": subtitle}})
    
    async def get_video(self, user_id):
        user = await self.col.find_one({"_id": int(user_id)})
        return user.get("video", "Encoded By @Codeflix_Bots") if user else "Encoded By @Codeflix_Bots"
    
    async def set_video(self, user_id, video):
        await self.col.update_one({"_id": int(user_id)}, {"$set": {"video": video}})

# Initialize database
db = Database()

# ==================== UTILITY FUNCTIONS ====================
def humanbytes(size):
    """Convert bytes to human readable format"""
    if not size:
        return "0 B"
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"

def TimeFormatter(milliseconds: int) -> str:
    """Convert milliseconds to readable time format"""
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "ᴅ, ") if days else "") + \
          ((str(hours) + "ʜ, ") if hours else "") + \
          ((str(minutes) + "ᴍ, ") if minutes else "") + \
          ((str(seconds) + "s, ") if seconds else "")
    return tmp[:-2] or "0 s"

async def progress_for_pyrogram(current, total, ud_type, message, start):
    now = time.time()
    diff = now - start
    if round(diff % 5.00) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff) * 1000
        time_to_completion = round((total - current) / speed) * 1000
        estimated_total_time = elapsed_time + time_to_completion

        elapsed_time = TimeFormatter(milliseconds=elapsed_time)
        estimated_total_time = TimeFormatter(milliseconds=estimated_total_time)

        progress = "{0}{1}".format(
            ''.join(["█" for _ in range(math.floor(percentage / 5))]),
            ''.join(["░" for _ in range(20 - math.floor(percentage / 5))])
        )
        
        tmp = progress + Txt.PROGRESS_BAR.format(
            round(percentage, 2),
            humanbytes(current),
            humanbytes(total),
            humanbytes(speed),
            estimated_total_time if estimated_total_time else "0 s"
        )
        
        try:
            await message.edit(
                text=f"{ud_type}\n\n{tmp}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("• ᴄᴀɴᴄᴇʟ •", callback_data="close")]
                ])
            )
        except:
            pass

# ==================== FILE PROCESSING FUNCTIONS ====================
def extract_season_episode(filename):
    """Extract season and episode numbers from filename"""
    patterns = [
        (r'S(\d+)(?:E|EP)(\d+)', ('season', 'episode')),
        (r'S(\d+)[\s-]*(?:E|EP)(\d+)', ('season', 'episode')),
        (r'Season\s*(\d+)\s*Episode\s*(\d+)', ('season', 'episode')),
        (r'\[S(\d+)\]\[E(\d+)\]', ('season', 'episode')),
        (r'S(\d+)[^\d]*(\d+)', ('season', 'episode')),
        (r'(?:E|EP|Episode)\s*(\d+)', (None, 'episode')),
        (r'\b(\d+)\b', (None, 'episode'))
    ]
    
    for pattern, (season_group, episode_group) in patterns:
        match = re.search(pattern, filename, re.IGNORECASE)
        if match:
            season = match.group(1) if season_group else None
            episode = match.group(2) if episode_group else match.group(1)
            return season, episode
    return None, None

def extract_quality(filename):
    """Extract quality information from filename"""
    quality_patterns = [
        (r'\b(\d{3,4}[pi])\b', lambda m: m.group(1)),  # 1080p, 720p
        (r'\b(4k|2160p)\b', lambda m: "4K"),
        (r'\b(2k|1440p)\b', lambda m: "2K"),
        (r'\b(HDRip|HDTV|WEB-DL|WEBRip|BluRay)\b', lambda m: m.group(1)),
        (r'\[(\d{3,4}[pi])\]', lambda m: m.group(1))
    ]
    
    for pattern, extractor in quality_patterns:
        match = re.search(pattern, filename, re.IGNORECASE)
        if match:
            return extractor(match)
    return "Unknown"

async def cleanup_files(*paths):
    """Safely remove files if they exist"""
    for path in paths:
        try:
            if path and os.path.exists(path):
                if os.path.isfile(path):
                    os.remove(path)
                elif os.path.isdir(path):
                    shutil.rmtree(path)
        except Exception as e:
            print(f"Error removing {path}: {e}")

async def process_thumbnail(thumb_path):
    """Process and resize thumbnail image"""
    if not thumb_path or not os.path.exists(thumb_path):
        return None
    
    try:
        with Image.open(thumb_path) as img:
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img.thumbnail((320, 320))
            img.save(thumb_path, "JPEG", quality=85)
        return thumb_path
    except Exception as e:
        print(f"Thumbnail processing error: {e}")
        await cleanup_files(thumb_path)
        return None

async def add_metadata_preserve_quality(input_path, output_path, user_id):
    """
    Add metadata WITHOUT re-encoding - preserves original quality
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    # Get metadata values
    title = await db.get_title(user_id)
    artist = await db.get_artist(user_id)
    author = await db.get_author(user_id)
    video_title = await db.get_video(user_id)
    audio_title = await db.get_audio(user_id)
    subtitle_title = await db.get_subtitle(user_id)
    
    # Get file extension
    file_ext = os.path.splitext(input_path)[1].lower()
    
    # For non-video/audio files, just copy
    if file_ext not in ['.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv', '.mp3', '.m4a', '.flac', '.wav', '.aac']:
        shutil.copy2(input_path, output_path)
        return output_path
    
    # Prepare FFmpeg command
    cmd = [
        'ffmpeg',
        '-i', input_path,
        '-c', 'copy',  # Copy all streams without re-encoding
        '-map', '0',
        '-map_metadata', '0',
    ]
    
    # Add metadata if provided
    if title and title.strip():
        cmd.extend(['-metadata', f'title={title}'])
    
    if artist and artist.strip():
        cmd.extend(['-metadata', f'artist={artist}'])
    
    if author and author.strip():
        cmd.extend(['-metadata', f'author={author}'])
    
    if video_title and video_title.strip():
        cmd.extend(['-metadata', f'video={video_title}'])
    
    if audio_title and audio_title.strip():
        cmd.extend(['-metadata', f'audio={audio_title}'])
    
    if subtitle_title and subtitle_title.strip():
        cmd.extend(['-metadata', f'subtitle={subtitle_title}'])
    
    # Add output file
    cmd.extend(['-y', output_path])
    
    try:
        # Execute FFmpeg
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            # Try simple copy as fallback
            shutil.copy2(input_path, output_path)
            return output_path
        
        # Verify file was created
        if os.path.exists(output_path):
            return output_path
        else:
            raise RuntimeError("Output file not created")
            
    except Exception as e:
        print(f"Error in add_metadata_preserve_quality: {e}")
        # Ultimate fallback: just copy the file
        shutil.copy2(input_path, output_path)
        return output_path

# ==================== BOT CLIENT ====================
# Create necessary directories
os.makedirs("downloads", exist_ok=True)
os.makedirs("temp", exist_ok=True)

# Initialize bot
app = Client(
    "auto_rename_bot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    workers=50,  # Reduced for Render
    sleep_threshold=30,
)

# ==================== HANDLERS ====================
# Start command
@app.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    user = message.from_user
    await db.add_user(user.id)
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("• ᴍʏ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs •", callback_data='help')],
        [
            InlineKeyboardButton('• ᴜᴘᴅᴀᴛᴇs', url='https://t.me/Codeflix_Bots'),
            InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ •', url='https://t.me/CodeflixSupport')
        ]
    ])
    
    if Config.START_PIC:
        await message.reply_photo(
            Config.START_PIC,
            caption=Txt.START_TXT.format(user.mention),
            reply_markup=buttons
        )
    else:
        await message.reply_text(
            Txt.START_TXT.format(user.mention),
            reply_markup=buttons
        )

# Help command
@app.on_message(filters.command("help") & filters.private)
async def help_handler(client, message):
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("• ᴀᴜᴛᴏ ʀᴇɴᴀᴍᴇ ғᴏʀᴍᴀᴛ •", callback_data='file_names')],
        [
            InlineKeyboardButton('• ᴛʜᴜᴍʙɴᴀɪʟ', callback_data='thumbnail'),
            InlineKeyboardButton('ᴄᴀᴘᴛɪᴏɴ •', callback_data='caption')
        ],
        [
            InlineKeyboardButton('• ᴍᴇᴛᴀᴅᴀᴛᴀ', callback_data='meta')
        ],
        [InlineKeyboardButton('• ʜᴏᴍᴇ', callback_data='home')]
    ])
    
    await message.reply_text(
        Txt.HELP_TXT,
        reply_markup=buttons,
        disable_web_page_preview=True
    )

# Autorename command
@app.on_message(filters.command("autorename") & filters.private)
async def autorename_handler(client, message):
    if len(message.command) < 2:
        await message.reply_text(
            "**Please provide a rename format!**\n\n"
            "**Example:** `/autorename {filename} [S{season}E{episode}] - {quality}`\n\n"
            "**Available variables:**\n"
            "- `{filename}`: Original filename\n"
            "- `{season}`: Season number\n"
            "- `{episode}`: Episode number\n"
            "- `{quality}`: Video quality\n"
            "- `{filesize}`: File size\n"
            "- `{duration}`: Duration (for videos)"
        )
        return
    
    format_template = message.text.split(" ", 1)[1]
    await db.set_format_template(message.from_user.id, format_template)
    
    await message.reply_text(
        f"**✅ Rename format set successfully!**\n\n"
        f"**Your format:** `{format_template}`\n\n"
        "Now send me any file to rename it automatically."
    )

# Main file handler - OPTIMIZED FOR RENDER
@app.on_message(filters.private & (filters.document | filters.video | filters.audio))
async def auto_rename_handler(client, message):
    user_id = message.from_user.id
    
    # Check if user has set rename format
    format_template = await db.get_format_template(user_id)
    if not format_template:
        await message.reply_text(
            "❌ Please set a rename format first!\n"
            "Use: `/autorename Your Format Here`\n\n"
            "**Example:** `/autorename {filename} [S{season}E{episode}]`"
        )
        return
    
    # Get file info
    if message.document:
        file_id = message.document.file_id
        file_name = message.document.file_name or "file"
        file_size = message.document.file_size
        media_type = "document"
        duration = 0
    elif message.video:
        file_id = message.video.file_id
        file_name = message.video.file_name or "video.mp4"
        file_size = message.video.file_size
        media_type = "video"
        duration = message.video.duration
    elif message.audio:
        file_id = message.audio.file_id
        file_name = message.audio.file_name or "audio.mp3"
        file_size = message.audio.file_size
        media_type = "audio"
        duration = message.audio.duration
    else:
        return
    
    # Extract filename components
    base_name = os.path.splitext(file_name)[0]
    ext = os.path.splitext(file_name)[1] or ('.mp4' if media_type == 'video' else '.mp3')
    
    season, episode = extract_season_episode(base_name)
    quality = extract_quality(base_name)
    
    # Replace variables in template
    new_filename = format_template
    replacements = {
        '{filename}': base_name,
        '{season}': season or '01',
        '{episode}': episode or '01',
        '{quality}': quality,
        '{filesize}': humanbytes(file_size),
        '{duration}': str(timedelta(seconds=duration)) if duration else '00:00:00',
        'Season': season or '01',
        'Episode': episode or '01',
        'QUALITY': quality.upper() if quality != "Unknown" else "HD"
    }
    
    for key, value in replacements.items():
        new_filename = new_filename.replace(key, value)
    
    new_filename = new_filename + ext
    
    # Download file
    msg = await message.reply_text("📥 **Downloading file...**")
    download_path = f"downloads/{user_id}_{int(time.time())}{ext}"
    
    try:
        # Download with progress
        start_time = time.time()
        file_path = await message.download(
            file_name=download_path,
            progress=progress_for_pyrogram,
            progress_args=("📥 Downloading...", msg, start_time)
        )
        
        if not os.path.exists(file_path):
            await msg.edit_text("❌ Download failed!")
            return
        
        # Get original file size
        original_size = os.path.getsize(file_path)
        await msg.edit_text(f"⚙️ **Processing file... (Size: {humanbytes(original_size)})**")
        
        # Process metadata if enabled
        output_path = file_path
        metadata_enabled = await db.get_metadata(user_id)
        
        # Check if file is video/audio for metadata
        is_video_audio = any(ext in file_path.lower() for ext in ['.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv', '.mp3', '.m4a', '.flac', '.wav', '.aac'])
        
        if metadata_enabled and is_video_audio:
            try:
                metadata_path = f"temp/{user_id}_metadata{ext}"
                await msg.edit_text("🔧 **Adding metadata...**")
                output_path = await add_metadata_preserve_quality(file_path, metadata_path, user_id)
                
                if os.path.exists(output_path) and output_path != file_path:
                    await cleanup_files(file_path)
            except Exception as e:
                print(f"Metadata error: {e}")
                output_path = file_path
        
        # Get thumbnail
        thumb_path = None
        user_thumb = await db.get_thumbnail(user_id)
        
        if user_thumb:
            thumb_path = f"temp/{user_id}_thumb.jpg"
            await client.download_media(user_thumb, file_name=thumb_path)
            thumb_path = await process_thumbnail(thumb_path)
        elif media_type == "video" and message.video.thumbs:
            thumb = message.video.thumbs[0]
            thumb_path = f"temp/{user_id}_video_thumb.jpg"
            await client.download_media(thumb.file_id, file_name=thumb_path)
            thumb_path = await process_thumbnail(thumb_path)
        
        # Get caption
        caption_template = await db.get_caption(user_id)
        if caption_template:
            caption = caption_template.replace("{filename}", new_filename)\
                                     .replace("{filesize}", humanbytes(file_size))\
                                     .replace("{duration}", str(timedelta(seconds=duration)) if duration else '00:00:00')
        else:
            caption = None
        
        # Get media type preference
        media_pref = await db.get_media_preference(user_id)
        
        # Get final output size
        final_size = os.path.getsize(output_path)
        await msg.edit_text(f"📤 **Uploading renamed file... (Final size: {humanbytes(final_size)})**")
        
        # Upload file based on media preference
        upload_start = time.time()
        
        # Check file type
        is_video_file = any(output_path.lower().endswith(ext) for ext in ['.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv', '.webm'])
        is_audio_file = any(output_path.lower().endswith(ext) for ext in ['.mp3', '.m4a', '.flac', '.wav', '.aac', '.ogg'])
        
        if media_pref == "document":
            await client.send_document(
                chat_id=message.chat.id,
                document=output_path,
                caption=caption,
                thumb=thumb_path,
                file_name=new_filename,
                progress=progress_for_pyrogram,
                progress_args=("📤 Uploading...", msg, upload_start)
            )
        elif media_pref == "video" and is_video_file:
            await client.send_video(
                chat_id=message.chat.id,
                video=output_path,
                caption=caption,
                thumb=thumb_path,
                duration=duration if duration > 0 else None,
                supports_streaming=True,
                progress=progress_for_pyrogram,
                progress_args=("📤 Uploading...", msg, upload_start)
            )
        elif media_pref == "audio" and is_audio_file:
            await client.send_audio(
                chat_id=message.chat.id,
                audio=output_path,
                caption=caption,
                thumb=thumb_path,
                duration=duration if duration > 0 else None,
                title=new_filename.rsplit('.', 1)[0],
                progress=progress_for_pyrogram,
                progress_args=("📤 Uploading...", msg, upload_start)
            )
        else:
            await client.send_document(
                chat_id=message.chat.id,
                document=output_path,
                caption=caption,
                thumb=thumb_path,
                file_name=new_filename,
                progress=progress_for_pyrogram,
                progress_args=("📤 Uploading...", msg, upload_start)
            )
        
        await msg.delete()
        
        await message.reply_text(
            f"✅ **File renamed successfully!**\n"
            f"**New name:** `{new_filename}`\n"
            f"**Original size:** {humanbytes(file_size)}\n"
            f"**Final size:** {humanbytes(final_size)}\n"
            f"**Sent as:** {media_pref.upper()}"
        )
        
    except Exception as e:
        await msg.edit_text(f"❌ **Error:** {str(e)[:200]}")
        print(f"Error: {e}")
    finally:
        # Cleanup
        await cleanup_files(
            download_path if 'download_path' in locals() else None,
            output_path if 'output_path' in locals() and output_path != file_path and os.path.exists(output_path) else None,
            thumb_path if 'thumb_path' in locals() and thumb_path and os.path.exists(thumb_path) else None
        )

# Callback query handler
@app.on_callback_query()
async def callback_handler(client, query):
    data = query.data
    user_id = query.from_user.id
    
    if data == "home":
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("• ᴍʏ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs •", callback_data='help')],
            [
                InlineKeyboardButton('• ᴜᴘᴅᴀᴛᴇs', url='https://t.me/Codeflix_Bots'),
                InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ •', url='https://t.me/CodeflixSupport')
            ]
        ])
        
        await query.message.edit_text(
            Txt.START_TXT.format(query.from_user.mention),
            reply_markup=buttons,
            disable_web_page_preview=True
        )
    
    elif data == "help":
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("• ᴀᴜᴛᴏ ʀᴇɴᴀᴍᴇ ғᴏʀᴍᴀᴛ •", callback_data='file_names')],
            [
                InlineKeyboardButton('• ᴛʜᴜᴍʙɴᴀɪʟ', callback_data='thumbnail'),
                InlineKeyboardButton('ᴄᴀᴘᴛɪᴏɴ •', callback_data='caption')
            ],
            [
                InlineKeyboardButton('• ᴍᴇᴛᴀᴅᴀᴛᴀ', callback_data='meta')
            ],
            [InlineKeyboardButton('• ʜᴏᴍᴇ', callback_data='home')]
        ])
        
        await query.message.edit_text(
            Txt.HELP_TXT,
            reply_markup=buttons,
            disable_web_page_preview=True
        )
    
    elif data == "file_names":
        format_template = await db.get_format_template(user_id) or "Not set"
        text = Txt.FILE_NAME_TXT + f"\n\n**Your current format:** `{format_template}`"
        await query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("• ʙᴀᴄᴋ", callback_data="help")]
            ]),
            disable_web_page_preview=True
        )
    
    elif data == "thumbnail":
        await query.message.edit_text(
            Txt.THUMBNAIL_TXT,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("• ʙᴀᴄᴋ", callback_data="help")]
            ]),
            disable_web_page_preview=True
        )
    
    elif data == "caption":
        await query.message.edit_text(
            Txt.CAPTION_TXT,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("• ʙᴀᴄᴋ", callback_data="help")]
            ]),
            disable_web_page_preview=True
        )
    
    elif data == "meta":
        metadata_status = await db.get_metadata(user_id)
        status_text = "ON ✅" if metadata_status else "OFF ❌"
        
        text = f"""
**㊋ Yᴏᴜʀ Mᴇᴛᴀᴅᴀᴛᴀ ɪs ᴄᴜʀʀᴇɴᴛʟʏ: {status_text}**

**◈ Tɪᴛʟᴇ ▹** `{await db.get_title(user_id)}`  
**◈ Aᴜᴛʜᴏʀ ▹** `{await db.get_author(user_id)}`  
**◈ Aʀᴛɪsᴛ ▹** `{await db.get_artist(user_id)}`  

**⚠️ Note:** Metadata addition does NOT re-encode or reduce quality.
        """
        
        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Turn ON", callback_data="metadata_on"),
                InlineKeyboardButton("Turn OFF", callback_data="metadata_off")
            ],
            [
                InlineKeyboardButton("How to Set Metadata", callback_data="metainfo")
            ],
            [
                InlineKeyboardButton("• ʙᴀᴄᴋ", callback_data="help")
            ]
        ])
        
        await query.message.edit_text(
            text=text,
            reply_markup=buttons,
            disable_web_page_preview=True
        )
    
    elif data == "metadata_on":
        await db.set_metadata(user_id, True)
        await query.answer("Metadata turned ON ✅", show_alert=True)
        await query.message.edit_text(
            "✅ **Metadata has been turned ON!**\n\n"
            "Now when you rename files, metadata will be added without re-encoding.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("• ʙᴀᴄᴋ", callback_data="meta")]
            ])
        )
    
    elif data == "metadata_off":
        await db.set_metadata(user_id, False)
        await query.answer("Metadata turned OFF ❌", show_alert=True)
        await query.message.edit_text(
            "❌ **Metadata has been turned OFF!**\n\n"
            "Files will be renamed without adding metadata.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("• ʙᴀᴄᴋ", callback_data="meta")]
            ])
        )
    
    elif data == "metainfo":
        await query.message.edit_text(
            text=Txt.META_TXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("• ʙᴀᴄᴋ", callback_data="meta"),
                    InlineKeyboardButton("• ᴄʟᴏsᴇ", callback_data="close")
                ]
            ])
        )
    
    elif data.startswith("media_"):
        media_type = data.split("_")[1]
        await db.set_media_preference(user_id, media_type)
        await query.answer(f"Media type set to {media_type.capitalize()} ✅", show_alert=True)
        
        await query.message.edit_text(
            f"✅ **Media type set to {media_type.upper()}!**\n\n"
            f"Renamed files will be sent as {media_type}s.\n\n"
            "**Note:** Video/Audio format only works for actual video/audio files.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("• ʙᴀᴄᴋ", callback_data="help")]
            ])
        )
    
    elif data == "close":
        await query.message.delete()
    
    else:
        await query.answer("Feature not implemented yet!", show_alert=True)

# ==================== RENDER WEB SERVER ====================
from aiohttp import web

async def web_server():
    web_app = web.Application(client_max_size=30000000)
    web_app.add_routes([web.get('/', lambda r: web.Response(text="Auto Rename Bot is Running!"))])
    return web_app

# ==================== MAIN ====================
if __name__ == "__main__":
    # Configure logging for Render
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Check for FFmpeg
    if not shutil.which("ffmpeg"):
        print("⚠️ WARNING: ffmpeg not found! Installing...")
        try:
            # Try to install ffmpeg
            os.system("apt-get update && apt-get install -y ffmpeg")
        except:
            print("Failed to install ffmpeg. Metadata features may not work.")
    else:
        print("✅ FFmpeg found")
    
    print("🚀 Starting Auto Rename Bot on Render...")
    print(f"🤖 Bot Token: {Config.BOT_TOKEN[:10]}...")
    print(f"👑 Admin IDs: {Config.ADMIN}")
    
    # Start web server in background for Render
    if Config.RENDER:
        print("🌐 Starting web server for Render...")
        import threading
        def run_web():
            web.run_app(web_server(), port=Config.PORT, host='0.0.0.0')
        
        web_thread = threading.Thread(target=run_web, daemon=True)
        web_thread.start()
    
    try:
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
