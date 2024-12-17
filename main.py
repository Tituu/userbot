import requests
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)

# Constants
TELEGRAM_BOT_TOKEN = "7440925694:AAGXftYiMZyocu-KCncSzBOtxKQUC5okgyU"
BLOGGER_API_KEY = "AIzaSyBlRLhbsLfrud7GUXsIW8bG59lu5PGDp7Q"
BLOG_ID = "1359530524392796723"

# Function to search for the movie in blog titles or labels
def search_blog(movie_name):
    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts?key={BLOGGER_API_KEY}"
    response = requests.get(url).json()

    if "items" in response:
        for post in response["items"]:
            title = post.get("title", "").lower()
            labels = [label.lower() for label in post.get("labels", [])] if "labels" in post else []

            if movie_name.lower() in title or movie_name.lower() in labels:
                return post.get("url")

    return None

# Command handler: Start
async def start(update: Update, context):
    await update.message.reply_text("Welcome! Send me a movie name, and I'll search for a blog post about it.")

# Message handler: Search for the movie
async def handle_message(update: Update, context):
    movie_name = update.message.text
    blog_url = search_blog(movie_name)

    if blog_url:
        await update.message.reply_text(f"I found a blog post: {blog_url}")
    else:
        await update.message.reply_text("Not found")

# Main function to set up the bot
def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()
