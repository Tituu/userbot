import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# --- Configurations ---
TELEGRAM_BOT_TOKEN = os.getenv("7518490388:AAHYoc_ua5nXEkEGOJotuL9qRZBFLdYNgzE")
BLOGGER_API_KEY = os.getenv("AIzaSyBlRLhbsLfrud7GUXsIW8bG59lu5PGDp7Q")
BLOG_ID = os.getenv("1359530524392796723")
WEBHOOK_URL = os.getenv("https://implicit-ashleigh-rahulpython-b9c90083.koyeb.app/") 

# --- Functions ---
def search_blogger_posts(query):
    search_url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts/search?q={query}&key={BLOGGER_API_KEY}"
    response = requests.get(search_url)
    
    if response.status_code == 200:
        posts = response.json().get('items', [])
        return posts
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Send me a movie name, and I'll find related blog posts for you!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    await update.message.reply_text(f"Searching for: {query}...")

    posts = search_blogger_posts(query)
    
    if posts:
        response_text = ""
        for post in posts[:5]:
            title = post.get('title', 'No Title')
            url = post.get('url', '#')
            response_text += f"🔹 [{title}]({url})\n"
        
        await update.message.reply_text(response_text, parse_mode='Markdown', disable_web_page_preview=False)
    else:
        await update.message.reply_text("Sorry, no posts found matching your query.")

async def set_webhook():
    webhook_url = f"{WEBHOOK_URL}/{TELEGRAM_BOT_TOKEN}"
    response = requests.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook?url={webhook_url}")
    if response.status_code == 200:
        print("Webhook set successfully!")
    else:
        print(f"Failed to set webhook: {response.text}")

def main():
    # Build the app
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).updater(None).build()

    # Add Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Set Webhook
    import asyncio
    asyncio.run(set_webhook())

    # Start Webhook Server
    app.run_webhook(
        listen="0.0.0.0", 
        port=int(os.environ.get('PORT', 8080)), 
        webhook_url=f"{WEBHOOK_URL}/{TELEGRAM_BOT_TOKEN}"
    )

if __name__ == "__main__":
    main()
