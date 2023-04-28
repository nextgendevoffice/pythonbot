import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, Filters

from config import TELEGRAM_BOT_TOKEN

logging.basicConfig(level=logging.INFO)

# Global variables to keep track of the broadcasting process
broadcast_groups = []
broadcast_step = 0
broadcast_message = ""

def start_broadcast(update: Update, context: CallbackContext):
    global broadcast_step
    print("start_broadcast called")
    if broadcast_step == 0:
        broadcast_step = 1
        update.message.reply_text('Please enter the group IDs that you want to broadcast (separated by commas).')
    else:
        update.message.reply_text('There is a task in progress. Please complete the current task before starting a new one.')

def process_text_message(update: Update, context: CallbackContext):
    process_message(update, context, update.message.text)

def process_image_message(update: Update, context: CallbackContext):
    process_message(update, context, update.message.photo)

def process_message(update: Update, context: CallbackContext, content):
    print("process_message called")
    global broadcast_step, broadcast_groups, broadcast_message

    if broadcast_step == 1:
        broadcast_groups = [int(group_id.strip()) for group_id in content.split(',')]
        broadcast_step = 2
        update.message.reply_text('Confirm Group IDs: {}\nPlease type the message or send an image you want to broadcast.'.format(broadcast_groups))
    elif broadcast_step == 2:
        successful_groups = []
        failed_groups = []

        if isinstance(content, list):
            caption = update.message.caption
            for group_id in broadcast_groups:
                try:
                    context.bot.send_photo(chat_id=group_id, photo=content[-1].file_id, caption=caption)
                    successful_groups.append(group_id)
                except Exception as e:
                    failed_groups.append(group_id)
                    update.message.reply_text(f"Error sending photo to group {group_id}: {e}")
        else:
            broadcast_message = content
            for group_id in broadcast_groups:
                try:
                    context.bot.send_message(chat_id=group_id, text=broadcast_message)
                    successful_groups.append(group_id)
                except Exception as e:
                    failed_groups.append(group_id)
                    update.message.reply_text(f"Error sending message to group {group_id}: {e}")

        update.message.reply_text("Broadcast complete. Sent to successful groups: {}\nFailed to send to groups: {}".format(successful_groups, failed_groups))
        broadcast_step = 0
        broadcast_groups = []
        broadcast_message = ""

def main():
    # Initialize the Updater with your bot token
    updater = Updater(TELEGRAM_BOT_TOKEN)

    # Add the command and message handlers to the dispatcher
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("broadcast", start_broadcast))
    dispatcher.add_handler(MessageHandler(Filters.text, process_text_message))
    dispatcher.add_handler(MessageHandler(Filters.photo, process_image_message))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
