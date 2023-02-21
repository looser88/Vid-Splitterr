import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)
import video_splitter as vs
import settings

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    logger.info("%s started the bot", user.first_name.title())
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!"
    )


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    message = f"""
        Hello {user.first_name}, welcome to Video Splitter by @yaw_o_k .
        Commands:
        /start : Start the bot
        /help : Show this information
        /split_size (args: seconds): Change split size seconds. eg /split_size 5 ie. Changes split size from 30 seconds(default) to 5 seconds
    """
    logger.info("%s started the bot", user.first_name.title())
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)


async def split_size(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.split(" ")[1]
    if int(user_input):
        settings.change_split_size(int(user_input))
        print(settings.SPLIT_SIZE)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Video split size has changed to {user_input}",
        )
        logger.info("Video split size changed to %s seconds", user_input)
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Wrong input. Enter a number instead.",
        )
        logger.info("Split size change attempt failed")


async def split(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Download file.
    file_id = update.message.video.file_id
    new_file = await context.bot.get_file(file_id)
    video_name = await new_file.download_to_drive("vid/video.mp4")
    logger.info("Saved %s ", video_name)

    # split
    split_videos = vs.split(str(video_name))

    for v in split_videos:
        await context.bot.send_video(chat_id=update.effective_chat.id, video=v)

    # Remove files to reuse folder
    vs.remove(split_videos)
    vs.remove([str(video_name)])
    logger.info("Removed %s and split videos", video_name)


if __name__ == "__main__":
    application = ApplicationBuilder().token(settings.BOT_TOKEN).build()

    start_handler = CommandHandler("start", start)
    split_size_handler = CommandHandler("split_size", split_size)
    video_handler = MessageHandler(filters.VIDEO, split)
    help_handler = CommandHandler("help", help)
    application.add_handler(start_handler)
    application.add_handler(video_handler)
    application.add_handler(split_size_handler)
    application.add_handler(help_handler)
    
    

    application.run_polling()
