from telegram.ext import ConversationHandler
from telegram import ReplyKeyboardMarkup


BASE_KEYBOARD = ReplyKeyboardMarkup([['/getmap', '/getweather'],
                                     ['/help', '/stop']],
                                    one_time_keyboard=False)
STOP_KEYBOARD = ReplyKeyboardMarkup([['/stop']],
                                    one_time_keyboard=False)


def start(update, context):
    update.message.reply_text(
        "Здравствуйте! Чтобы начать работу, отправьте команду /help",
        reply_markup=BASE_KEYBOARD)


def bot_help(update, context):
    doc = """
    Список команд:
    • /getmap - получить карту заданного места
    • /getweather - получить данные о погоде
    • /stop - остановить выполнение любой задачи
    """
    update.message.reply_text(doc)


def stop(update, context):
    update.message.reply_text("Задача остановлена.")
    context.user_data.clear()
    return ConversationHandler.END