import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from instaloader import Instaloader, Post
import logging
import time

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram Bot Token (from environment variable)
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Initialize Instaloader
loader = Instaloader()

def start(update, context):
    update.message.reply_text('Bhai! Instagram Reels download karne ke liye mujhe Reel ka URL bhej de. /help ke liye commands dekho!')

def help_command(update, context):
    update.message.reply_text('Commands:\n/start - Bot shuru karo\n/help - Yeh menu dekho\nBhejna - Instagram Reel URL (e.g., https://www.instagram.com/reel/abc123/)')

def download_reel(update, context):
    url = update.message.text
    chat_id = update.message.chat_id

    try:
        logger.info(f"Received URL: {url}")
        update.message.reply_text('Thodi der ruk, Reel download kar raha hu...')

        # Extract shortcode from URL
        shortcode = url.split('/reel/')[-1].split('/')[0]
        
        # Fetch the post
        post = Post.from_shortcode(loader.context, shortcode)
        
        # Download the video
        video_url = post.video_url
        if not video_url:
            update.message.reply_text('Bhai, yeh Reel download nahi ho saka. Public Reel check karo!')
            return

        # Download video using Instaloader
        loader.download_post(post, target=f"{chat_id}")
        
        # Send the downloaded video
        with open(f'{chat_id}/{post.shortcode}_REEL.mp4', 'rb') as video:
            context.bot.send_video(chat_id=chat_id, video=video)

        # Clean up
        for file in os.listdir(f'{chat_id}'):
            os.remove(os.path.join(f'{chat_id}', file))
        os.rmdir(f'{chat_id}')
        logger.info(f"Sent reel to {chat_id}")

    except Exception as e:
        logger.error(f"Error: {e}")
        update.message.reply_text('Bhai, kuch gadbad ho gaya. Sahi URL bhej ya thodi der baad try kar.')

def main():
    if not TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables!")
        return

    # Ensure only one instance runs
    logger.info("Starting bot with a delay to avoid conflict...")
    time.sleep(5)  # Delay to allow previous instance to terminate

    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, download_reel))

    logger.info("Bot is starting...")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
