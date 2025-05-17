import logging

import telegram

from config import BOT_TOKEN
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import sqlite3

CHOOSE_PET, INTERACT = 0, 1
TIMER = 3600

pets = {}
con = sqlite3.connect("data/bd/tamagoni.db")
cur = con.cursor()
ACTIONS = ["Кормить", "Мыть", "Гулять", "Спать", "Сражаться."]
bot = telegram.Bot(token=BOT_TOKEN)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    reply_keyboard = [["Огонь", "Вода", "Таракан", "Воздух"]]
    await bot.send_photo(chat_id=user.id, photo="data/image/bug.png")
    await update.message.reply_text(
        "Привет! Выбери себе питомца:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )

    return CHOOSE_PET

async def choose_pet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    pet = update.message.text
    result = cur.execute("""SELECT * FROM pets
                WHERE name = ?""", (pet,)).fetchall()
    pets[user.id] = {
        "type": pet,
        "lvl": 0,
        "exp": 0,
        "element": result[0][2],
        "damage": result[0][3],
        "armor": result[0][4],
        "helth": result[0][5],
        "hunger": 0,
        "cleanliness": 0,
        "happiness": 0,
        "energy": 0,
    }
    await update.message.reply_text(
        f"Ты выбрал {pet}!\nТы можешь: Кормить, Мыть, Гулять, Спать, Сражаться.\nЧто хочешь сделать?",
        reply_markup=ReplyKeyboardMarkup([ACTIONS], resize_keyboard=True)
    )
    return INTERACT


class Food():
    def __init__(self, update, context):
        self.update = update
        self.context = context
    async def task_food(self, context):
        """Выводит сообщение"""
        await context.bot.send_message(context.job.chat_id, text=f'Твой питомец проголодался!')
        user = self.update.message.from_user
        pet = pets.get(user.id)
        pet["hunger"] = max(pet["hunger"] - 2, 0)

    async def set_timer_food(self, update, context):
        """Добавляем задачу в очередь"""
        chat_id = update.effective_message.chat_id
        # Добавляем задачу в очередь
        context.job_queue.run_once(self.task_food, TIMER, chat_id=chat_id, name=str(chat_id), data=TIMER)

        text = 'ok'
        await update.effective_message.reply_text(text)


class Sleep():
    def __init__(self, update, context):
        self.update = update
        self.context = context
    async def task_sleep(self, context):
        """Выводит сообщение"""
        await context.bot.send_message(context.job.chat_id, text=f'Твой питомец устал!')
        user = self.update.message.from_user
        pet = pets.get(user.id)
        pet["energy"] = max(pet["energy"] - 2, 0)

    async def set_timer_sleep(self, update, context):
        """Добавляем задачу в очередь"""
        chat_id = update.effective_message.chat_id
        # Добавляем задачу в очередь
        context.job_queue.run_once(self.task_sleep, TIMER, chat_id=chat_id, name=str(chat_id), data=TIMER)

        text = 'ok'
        await update.effective_message.reply_text(text)


class Walk():
    def __init__(self, update, context):
        self.update = update
        self.context = context
    async def task_walk(self, context):
        """Выводит сообщение"""
        await context.bot.send_message(context.job.chat_id, text=f'Твой питомец скучает!')
        user = self.update.message.from_user
        pet = pets.get(user.id)
        pet["happiness"] = max(pet["happiness"] - 2, 0)

    async def set_timer_walk(self, update, context):
        """Добавляем задачу в очередь"""
        chat_id = update.effective_message.chat_id
        # Добавляем задачу в очередь
        context.job_queue.run_once(self.task_walk, TIMER, chat_id=chat_id, name=str(chat_id), data=TIMER)

        text = 'ok'
        await update.effective_message.reply_text(text)


class Wash():
    def __init__(self, update, context):
        self.update = update
        self.context = context
    async def task_wash(self, context):
        """Выводит сообщение"""
        await context.bot.send_message(context.job.chat_id, text=f'Твой питомец испачкался!')
        user = self.update.message.from_user
        pet = pets.get(user.id)
        pet["cleanliness"] = max(pet["cleanliness"] - 2, 0)

    async def set_timer_wash(self, update, context):
        """Добавляем задачу в очередь"""
        chat_id = update.effective_message.chat_id
        # Добавляем задачу в очередь
        context.job_queue.run_once(self.task_wash, TIMER, chat_id=chat_id, name=str(chat_id), data=TIMER)

        text = 'ok'
        await update.effective_message.reply_text(text)


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
        a = Food(update, context)
        await a.set_timer_food(update, context)
    elif action == "Мыть":
        pet["cleanliness"] = min(pet["cleanliness"] + 2, 10)
        response = "Теперь он чистенький!"
        g = Wash(update, context)
        await g.set_timer_wash(update, context)
    elif action == "Гулять":
        pet["happiness"] = min(pet["happiness"] + 2, 10)
        pet["energy"] = max(pet["energy"] - 1, 0)
        response = "Он нагулялся!"
        v = Walk(update, context)
        await v.set_timer_walk(update, context)
    elif action == "Спать":
        pet["energy"] = min(pet["energy"] + 2, 10)
        response = "Он выспался!"
        b = Sleep(update, context)
        await b.set_timer_sleep(update, context)
    else:
        response = "Неизвестная команда."

    status = f"""Состояние {pet['type']}:
 Уровень: {pet["lvl"]}
 Опыт: {pet["exp"]}
 Стихия: {pet["element"]}
 Урон: {pet["damage"]}
 Броня: {pet["armor"]}
 Здоровье: {pet["helth"]}
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