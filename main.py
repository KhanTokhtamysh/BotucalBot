# !/usr/bin/env python
# pylint: disable=C0116,W0613
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

# Enable logging
# logging.basicConfig(filename='logfile.log',
#                     filemode='a',
#                     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#                     level=logging.INFO
# )
logging.basicConfig(
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO
)

logger = logging.getLogger(__name__)

GENDER, PHOTO, LOCATION, BIO = range(4)


def start(update: Update, context: CallbackContext) -> int:
    """Starts the conversation and asks the user about their gender."""
    reply_keyboard = [['Лёша', 'Олексейко', 'Тростников']]

    update.message.reply_text(
        'Привет! Я твой тестировочный бот. '
        'Нажми /cancel чтобы я замолчал.\n\n'
        'А какой ты сегодня?',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Boy or Girl?'
        ),
    )

    return GENDER


def gender(update: Update, context: CallbackContext) -> int:
    """Stores the selected gender and asks for a photo."""
    user = update.message.from_user
    logger.info("Gender of %s: %s", user.first_name, update.message.text)
    update.message.reply_text(
        'Ого! Вышли мне своё фото, хочу посмотреть, как ты выглядишь. '
        'или нажми /skip , если не хочешь.',
        reply_markup=ReplyKeyboardRemove(),
    )

    return PHOTO


def photo(update: Update, context: CallbackContext) -> int:
    """Stores the photo and asks for a location."""
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    photo_file.download(f'media/download/{user.first_name}.jpg')
    logger.info("Photo of %s: %s", user.first_name, f'{user.first_name}.jpg')
    update.message.reply_text(
        'Красивое! А теперь пришли мне свою Геолокацию. Или нажми /skip , если не хочешь.'
    )

    return LOCATION

def skip_photo(update: Update, context: CallbackContext) -> int:
    """Skips the photo and asks for a location."""
    user = update.message.from_user
    logger.info("User %s did not send a photo.", user.first_name)
    update.message.reply_text(
        'Уверен, что ты выглядишь замечательно! А теперь пришли мне свою Геолокацию. Или нажми /skip , если не хочешь.'
    )

    return LOCATION


def location(update: Update, context: CallbackContext) -> int:
    """Stores the location and asks for some info about the user."""
    user = update.message.from_user
    user_location = update.message.location
    logger.info(
        "Location of %s: %f / %f", user.first_name, user_location.latitude, user_location.longitude
    )
    update.message.reply_text(
        'Так мне проще будет найти тебя! Теперь расскажи мне о себе.'
    )

    return BIO


def skip_location(update: Update, context: CallbackContext) -> int:
    """Skips the location and asks for info about the user."""
    user = update.message.from_user
    logger.info("User %s did not send a location.", user.first_name)
    update.message.reply_text(
        'Да ты чего? Не бойся! Хотя бы расскажи мне что-нибудь о себе.'
    )

    return BIO


def bio(update: Update, context: CallbackContext) -> int:
    """Stores the info about the user and ends the conversation."""
    user = update.message.from_user
    logger.info("Bio of %s: %s", user.first_name, update.message.text)
    update.message.reply_text('Спасибо! Надеюсь, мы еще свяжемся. Нажми /start , чтобы начать снова.')

    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Пока! Надеюсь, мы еще свяжемся. Нажми /start , чтобы начать снова.', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("868924169:AAH0eJnLA2PYw45pCE7i_7uGcKXXG1fa4Og")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            GENDER: [MessageHandler(Filters.regex('^(Лёша|Олексейко|Тростников)$'), gender)],
            PHOTO: [MessageHandler(Filters.photo, photo), CommandHandler('skip', skip_photo)],
            LOCATION: [
                MessageHandler(Filters.location, location),
                CommandHandler('skip', skip_location),
            ],
            BIO: [MessageHandler(Filters.text & ~Filters.command, bio)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()


