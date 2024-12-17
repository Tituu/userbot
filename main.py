import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Constants
TELEGRAM_BOT_TOKEN = "7518490388:AAHFxpu_qwJ0ojYjS7_CX1xjIahtamE-miw"
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

# Telegram bot command handlers
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Welcome! Send me a movie name, and I'll search for a blog post about it.")

def handle_message(update: Update, context: CallbackContext):
    movie_name = update.message.text
    blog_url = search_blog(movie_name)

    if blog_url:
        update.message.reply_text(f"I found a blog post: {blog_url}")
    else:
        update.message.reply_text("Not found")

def main():
    updater = Updater(TELEGRAM_BOT_TOKEN)
    dispatcher = updater.dispatcher

    # Add handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
