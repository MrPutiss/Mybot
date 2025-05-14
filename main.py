import logging
from config import BOT_TOKEN
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

CHOOSE_PET, INTERACT = 0, 1

pets = {}

ACTIONS = ["Кормить", "Мыть", "Гулять", "Спать"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [["Кот", "Собака", "Дракончик"]]
    await update.message.reply_text(
        "Привет! Выбери себе питомца:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return CHOOSE_PET

async def choose_pet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    pet = update.message.text
    pets[user.id] = {
        "type": pet,
        "hunger": 5,
        "cleanliness": 5,
        "happiness": 5,
        "energy": 5,
    }
    await update.message.reply_text(
        f"Ты выбрал {pet}!\nТы можешь: Кормить, Мыть, Гулять, Спать.\nЧто хочешь сделать?",
        reply_markup=ReplyKeyboardMarkup([ACTIONS], resize_keyboard=True)
    )
    return INTERACT

async def interact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    action = update.message.text
    pet = pets.get(user.id)

    if not pet:
        await update.message.reply_text("Сначала выбери питомца с помощью /start")
        return ConversationHandler.END

    if action == "Кормить":
        pet["hunger"] = min(pet["hunger"] + 2, 10)
        response = "Ты покормил питомца. Он доволен!"
    elif action == "Мыть":
        pet["cleanliness"] = min(pet["cleanliness"] + 2, 10)
        response = "Теперь он чистенький!"
    elif action == "Гулять":
        pet["happiness"] = min(pet["happiness"] + 2, 10)
        pet["energy"] = max(pet["energy"] - 1, 0)
        response = "Он нагулялся!"
    elif action == "Спать":
        pet["energy"] = min(pet["energy"] + 3, 10)
        response = "Он выспался!"
    else:
        response = "Неизвестная команда."

    status = f"""Состояние {pet['type']}:
 Сытость: {pet['hunger']}
 Чистота: {pet['cleanliness']}
 Счастье: {pet['happiness']}
 Энергия: {pet['energy']}"""

    await update.message.reply_text(response + "\n\n" + status)
    return INTERACT

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("")
    return ConversationHandler.END

def main():
    import os
    TOKEN = BOT_TOKEN

    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSE_PET: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_pet)],
            INTERACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, interact)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()