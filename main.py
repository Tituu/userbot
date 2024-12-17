import os
import requests
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv("7518490388:AAHFxpu_qwJ0ojYjS7_CX1xjIahtamE-miw")  # Set this in your Koyeb environment
BLOGGER_API_KEY = os.getenv("AIzaSyBlRLhbsLfrud7GUXsIW8bG59lu5PGDp7Q")  # Set this in your Koyeb environment
BLOG_ID = os.getenv("1359530524392796723")  # Set this in your Koyeb environment
APP_URL = os.getenv("https://tituu.koyeb.app/")  # Your deployed Koyeb app URL

# Initialize Flask app and Telegram bot
app = Flask(__name__)
bot = Bot(token=TELEGRAM_BOT_TOKEN)

# Initialize the Application
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()


async def fetch_blog_post(movie_name):
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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the /start command to greet the user.
    """
    await update.message.reply_text("Welcome to the Movie Blog Fetcher Bot! Send me a movie name to find related blog posts.")


async def fetch_movie_blog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the user's message containing a movie name.
    """
    movie_name = update.message.text.strip()
    if movie_name:
        result = await fetch_blog_post(movie_name)
        await update.message.reply_text(result)
    else:
        await update.message.reply_text("Please provide a movie name!")


# Add command handlers to the application
application.add_handler(CommandHandler("start", start))


@app.route(f"/{TELEGRAM_BOT_TOKEN}", methods=["POST"])
def webhook():
    """
    Receives updates from Telegram and dispatches them to the bot.
    """
    update = Update.de_json(request.get_json(force=True), bot)
    application.update_queue.put_nowait(update)
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
