import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from telegram.error import Conflict
import requests

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(name)

# Environment variables
TELEGRAM_BOT_TOKEN = os.getenv("7518490388:AAHFxpu_qwJ0ojYjS7_CX1xjIahtamE-miw")
BLOGGER_API_KEY = os.getenv("AIzaSyBlRLhbsLfrud7GUXsIW8bG59lu5PGDp7Q")
BLOG_ID = os.getenv("1359530524392796723")
WEBHOOK_URL = os.getenv("implicit-ashleigh-rahulpython-b9c90083.koyeb.app/")  # Use the Koyeb app URL

# Function to search Blogger posts
def search_blogger_posts(query):
    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts"
    params = {"key": BLOGGER_API_KEY, "q": query}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        posts = response.json().get("items", [])
        return posts
    except requests.RequestException as e:
        logger.error(f"Error searching Blogger: {e}")
        return []

# Command handler for /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome! Send me a movie name, and I'll find related blog posts for you."
    )

# Message handler for movie search
async def search_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    await update.message.reply_text(f"Searching for '{query}'...")

    # Search for posts on Blogger
    posts = search_blogger_posts(query)

    if posts:
        response_message = "Here are the related blog posts I found:\n\n"
        for post in posts:
            title = post.get("title")
            url = post.get("url")
            response_message += f"{title}\n{url}\n\n"
        await update.message.reply_text(response_message)
    else:
        await update.message.reply_text("Sorry, no related blog posts were found.")

# Main function
async def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_movie))

    # Set webhook
    logger.info("Setting webhook...")
    try:
        await app.bot.set_webhook(WEBHOOK_URL)
        logger.info(f"Webhook set to {WEBHOOK_URL}")
    except Conflict:
        logger.warning("Webhook already set by another bot instance.")

    # Start the webhook server
    app.run_webhook(
        listen="0.0.0.0",
        port=8080,
        webhook_url=WEBHOOK_URL,
    )


if name == "main":
    import asyncio
    asyncio.run(main())
