import os
import requests
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Dispatcher, CommandHandler

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv("7518490388:AAHFxpu_qwJ0ojYjS7_CX1xjIahtamE-miw")  # Set this in your Koyeb environment
BLOGGER_API_KEY = os.getenv("AIzaSyBlRLhbsLfrud7GUXsIW8bG59lu5PGDp7Q")  # Set this in your Koyeb environment
BLOG_ID = os.getenv("1359530524392796723")  # Set this in your Koyeb environment
APP_URL = os.getenv("https://tituu.koyeb.app/")  # Your deployed Koyeb app URL

# Initialize Flask app and bot
app = Flask(__name__)
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dispatcher = Dispatcher(bot, None, workers=0)


def fetch_blog_post(movie_name):
    """
    Fetches a blog post link from Blogger that matches the given movie name 
    in the title or label.

    Args:
        movie_name (str): The name of the movie to search for.

    Returns:
        str: The blog post link or a 'Not found' message.
    """
    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts/search?q={movie_name}&key={BLOGGER_API_KEY}"
    response = requests.get(url)

    if response.status_code == 200:
        posts = response.json().get("items", [])
        if posts:
            return f"Found blog post: {posts[0].get('url', 'Not found')}"
        else:
            return f"No blog post found for the movie: {movie_name}"
    else:
        return f"Error: {response.status_code} - {response.text}"


def start(update: Update, context):
    """
    Handles the /start command to greet the user.
    """
    update.message.reply_text("Welcome to the Movie Blog Fetcher Bot! Send me a movie name to find related blog posts.")


def fetch_movie_blog(update: Update, context):
    """
    Handles the user's message containing a movie name.
    """
    movie_name = update.message.text.strip()
    if movie_name:
        result = fetch_blog_post(movie_name)
        update.message.reply_text(result)
    else:
        update.message.reply_text("Please provide a movie name!")


# Add command handlers
dispatcher.add_handler(CommandHandler("start", start))


@app.route(f"/{TELEGRAM_BOT_TOKEN}", methods=["POST"])
def webhook():
    """
    Receives updates from Telegram and dispatches them to the bot.
    """
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK", 200


@app.route("/set_webhook", methods=["GET", "POST"])
def set_webhook():
    """
    Sets the webhook for Telegram.
    """
    webhook_url = f"{APP_URL}/{TELEGRAM_BOT_TOKEN}"
    success = bot.set_webhook(url=webhook_url)
    if success:
        return f"Webhook set to {webhook_url}", 200
    else:
        return "Failed to set webhook", 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
