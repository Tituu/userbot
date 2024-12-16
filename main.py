from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from googleapiclient.discovery import build
import logging

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Constants
TELEGRAM_BOT_TOKEN = "7518490388:AAHFxpu_qwJ0ojYjS7_CX1xjIahtamE-miw"
BLOGGER_API_KEY = "AIzaSyBlRLhbsLfrud7GUXsIW8bG59lu5PGDp7Q"
BLOG_ID = "1359530524392796723"

# Function to search for posts in Blogger
def search_blogger_posts(query):
    service = build("blogger", "v3", developerKey=BLOGGER_API_KEY)
    try:
        response = service.posts().list(blogId=BLOG_ID, q=query).execute()
        posts = response.get("items", [])
        return posts
    except Exception as e:
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

# Main function to start the bot
def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_movie))

    # Start the bot
    logger.info("Bot started!")
    app.run_polling()

if __name__ == "__main__":
    main()
