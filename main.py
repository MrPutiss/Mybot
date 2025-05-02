import logging
from telegram.ext import Application, MessageHandler, filters
from telegram.ext import CommandHandler
from config import BOT_TOKEN
from telegram import ReplyKeyboardMarkup

# Запускаем логгирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)



async def help(update, context):
    await update.message.reply_text(
        "Я бот справочник.")


async def feed(update, context):
    await update.message.reply_text(
        "Я все сделаю, честно")


async def pet(update, context):
    await update.message.reply_text("Я все сделаю, честно")


async def play(update, context):
    await update.message.reply_text(
        "Я все сделаю, честно")


async def walk(update, context):
    await update.message.reply_text(
        "Я все сделаю, честно")



def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("feed", feed))
    application.add_handler(CommandHandler("pet", pet))
    application.add_handler(CommandHandler("play", play))
    application.add_handler(CommandHandler("walk", walk))
    application.add_handler(CommandHandler("help", help))

    reply_keyboard = [['/feed', '/pet'],
                      ['/play', '/walk']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)

    async def start(update, context):
        if update.message.text == "/start":
            await update.message.reply_text(
                "Я бот-тамагочи, выбери себе питомца",
                reply_markup=markup
            )
        else:
            await update.message.reply_text(
                "?")
    text_handler = MessageHandler(filters.TEXT, start)

    application.add_handler(text_handler)


    application.run_polling()


if __name__ == '__main__':
    main()