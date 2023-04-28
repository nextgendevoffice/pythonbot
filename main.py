import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext
from telegram.ext.filters import Filters

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

def process_message(update: Update, context: CallbackContext):
    print("process_message called")
    global broadcast_step, broadcast_groups, broadcast_message
    text = update.message.text

    if broadcast_step == 1:
        broadcast_groups = [int(group_id.strip()) for group_id in text.split(',')]
        broadcast_step = 2
        update.message.reply_text('Confirm Group IDs: {}\nPlease type the message you want to broadcast.'.format(broadcast_groups))
    elif broadcast_step == 2:
        broadcast_message = text
        for group_id in broadcast_groups:
            try:
                context.bot.send_message(chat_id=group_id, text=broadcast_message)
            except Exception as e:
                update.message.reply_text(f"Error sending message to group {group_id}: {e}")
        update.message.reply_text("Broadcast complete.")
        broadcast_step = 0
        broadcast_groups = []
        broadcast_message = ""

def main() -> None:
    updater = Updater(TELEGRAM_BOT_TOKEN)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("broadcast", start_broadcast))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, process_message))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

