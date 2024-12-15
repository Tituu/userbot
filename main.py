from telethon import TelegramClient, events, Button
from pytube import YouTube
from yt_dlp import YoutubeDL
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
import os
import time

# Your API ID and Hash
API_ID = '21575315'
API_HASH = 'acdbe0573a6babdf1dfa88d113ed02c3'

# Your Spotify API credentials
SPOTIFY_CLIENT_ID = 'YOUR_SPOTIFY_CLIENT_ID'
SPOTIFY_CLIENT_SECRET = 'YOUR_SPOTIFY_CLIENT_SECRET'

# Your Telegram User ID
OWNER_ID = 7654734465  # Replace with your Telegram User ID

# Log channel ID
LOG_CHANNEL_ID = '-1002340678637'  # Replace with your log channel ID

# Initialize Spotify client
sp = Spotify(client_credentials_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET))

# Create the Telegram Client
client = TelegramClient('userbot', API_ID, API_HASH)

# Track user message timestamps for spam detection
user_message_timestamps = {}

# Custom auto-reply
AUTO_REPLY = "Hi, I'm currently unavailable. I'll get back to you soon!"

# Helper function to mute a user
async def mute_user(chat_id, user_id):
    try:
        await client.edit_permissions(chat_id, user_id, send_messages=False)
    except Exception as e:
        print(f"Failed to mute user {user_id}: {e}")

# Helper function to unmute a user
async def unmute_user(chat_id, user_id):
    try:
        await client.edit_permissions(chat_id, user_id, send_messages=True)
    except Exception as e:
        print(f"Failed to unmute user {user_id}: {e}")

# Show available commands
@client.on(events.NewMessage(pattern=r'\.cmd'))
async def show_commands(event):
    commands = """
**Available Commands:**
1. `.cmd` - Show this list of commands.
2. `/ping` - Test the bot's response time.
3. `/broadcast <message>` - Send a message to all private chats (owner only).
4. `/spotify <song or artist>` - Download music using Spotify metadata.
5. `/post <caption> | <Button1:URL1, Button2:URL2>` - Post a message with a photo and buttons.
6. `/download <YouTube URL>` - Download video or audio from YouTube.
"""
    await event.reply(commands)

# Start the bot
@client.on(events.NewMessage(incoming=True))
async def monitor_messages(event):
    if event.is_private:  # Auto-reply for private messages
        await event.reply(AUTO_REPLY)
        return

    # Detect spamming in group chats
    chat_id = event.chat_id
    user_id = event.sender_id

    # Get current time
    current_time = time.time()

    # Update user message timestamps
    if user_id not in user_message_timestamps:
        user_message_timestamps[user_id] = []
    user_message_timestamps[user_id].append(current_time)

    # Filter timestamps to the last 3 seconds
    user_message_timestamps[user_id] = [
        t for t in user_message_timestamps[user_id] if current_time - t <= 3
    ]

    # Check if user has sent more than 4 messages in the last 3 seconds
    if len(user_message_timestamps[user_id]) > 4:
        # Mute the user
        await mute_user(chat_id, user_id)

        # Log the incident in the log channel with an unmute button
        await client.send_message(
            LOG_CHANNEL_ID,
            f"⚠️ User [ID: {user_id}](tg://user?id={user_id}) was muted in chat {chat_id} for spamming.",
            buttons=[
                Button.inline("🔊 Unmute User", data=f"unmute:{chat_id}:{user_id}")
            ],
        )
        await event.reply("🚫 You have been muted for spamming.")

# Callback handler for unmute button
@client.on(events.CallbackQuery(pattern=r"unmute:(-?\d+):(\d+)"))
async def unmute_callback(event):
    chat_id = int(event.pattern_match.group(1))
    user_id = int(event.pattern_match.group(2))

    # Unmute the user
    await unmute_user(chat_id, user_id)

    # Acknowledge the unmute action
    await event.edit("✅ User has been unmuted.")

# Command: Post a message with photo and buttons
@client.on(events.NewMessage(pattern='/post'))
async def post_message(event):
    if event.sender_id != OWNER_ID:  # Check if the user is the owner
        await event.reply("You are not authorized to use this command.")
        return

    # Example usage: /post Caption | Button1:URL1, Button2:URL2
    try:
        content = event.raw_text.split(' ', 1)[1]
        parts = content.split('|')
        caption = parts[0].strip()
        buttons_data = parts[1].strip().split(',')

        buttons = [
            Button.url(button.strip().split(':')[0], button.strip().split(':')[1])
            for button in buttons_data
        ]

        # Upload a photo (example: replace 'photo.jpg' with your image file)
        photo_path = 'photo.jpg'  # Replace with the actual path to the photo
        if not os.path.exists(photo_path):
            await event.reply("Photo not found. Please upload a valid image.")
            return

        await client.send_file(
            event.chat_id,
            file=photo_path,
            caption=caption,
            buttons=buttons
        )
    except IndexError:
        await event.reply("Invalid format. Use: `/post Caption | Button1:URL1, Button2:URL2`")
    except Exception as e:
        await event.reply(f"Failed to post message: {e}")

# Command: Download YouTube video or music
@client.on(events.NewMessage(pattern='/download (.+)'))
async def download(event):
    url = event.pattern_match.group(1)
    try:
        yt = YouTube(url)
        stream = yt.streams.filter(progressive=True, file_extension='mp4').first()
        filename = stream.download(output_path='downloads')
        await event.reply(f"Downloaded successfully: {filename}")
    except Exception as e:
        await event.reply(f"Failed to download: {e}")

# Command: Spotify Music Downloader
@client.on(events.NewMessage(pattern='/spotify (.+)'))
async def spotify_download(event):
    query = event.pattern_match.group(1)
    try:
        # Search for the track on Spotify
        result = sp.search(q=query, type='track', limit=1)
        if not result['tracks']['items']:
            await event.reply("No track found on Spotify.")
            return
        
        track = result['tracks']['items'][0]
        track_name = track['name']
        artist = track['artists'][0]['name']
        track_url = track['external_urls']['spotify']
        search_query = f"{track_name} {artist}"

        await event.reply(f"Found track: {track_name} by {artist}\nDownloading...")

        # Use yt-dlp to download the track from YouTube
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'downloads/{track_name}.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"ytsearch1:{search_query}"])

        await event.reply(f"Downloaded successfully: {track_name} by {artist}")
    except Exception as e:
        await event.reply(f"Failed to download: {e}")

# Welcome new channel members
@client.on(events.ChatAction)
async def welcome_user(event):
    if event.user_joined or event.user_added:
        user = await event.get_user()
        chat = await event.get_chat()

        welcome_message = await client.send_message(
            chat.id,
            f"🎉 Welcome [@{user.username}](tg://user?id={user.id}) to {chat.title}!",
            parse_mode="md"
        )

        # Delete welcome message after 5-10 seconds
        await asyncio.sleep(5)
        await welcome_message.delete()

        # Log the join event in the log channel
        await client.send_message(
            LOG_CHANNEL_ID,
            f"👤 New user joined: [@{user.username}](tg://user?id={user.id}) in {chat.title}.",
            parse_mode="md"
        )

# Start the client
print("Userbot is running...")
client.start()
client.run_until_disconnected()
