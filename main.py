import logging
import requests
from telegram.ext import Updater, Filters
from telegram.ext import CommandHandler, ConversationHandler, MessageHandler
from telegram import ReplyKeyboardMarkup


logging.basicConfig(filename='telegram_bot.log',
                    filemode='w',
                    format='%(asctime)s - %(name)s -'
                           '%(levelname)s - %(message)s',
                    level=logging.DEBUG)

logger = logging.getLogger(__name__)

TOKEN = ""
APIKEY = ""
ASKZM, ASKPLC = range(2)
BASE_KEYBOARD = ReplyKeyboardMarkup([['/getmap'], ['/help', '/stop']],
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
    • /stop - остановить выполнение любой задачи
    """
    update.message.reply_text(doc)


def stop(update, context):
    update.message.reply_text("Задача остановлена.")
    context.user_data.clear()
    return ConversationHandler.END


def getmap(update, context):
    """Узнать геопозицию человека на карте"""
    update.message.reply_text("Введите искомый адрес.")
    return ASKPLC


def ask_place(update, context):
    context.user_data['place'] = update.message.text
    update.message.reply_text("Задайте параметр приближения " +
                              "(целое цисло от 2 до 21).")
    return ASKZM


def ask_zoom(update, context):
    geocode = context.user_data['place']
    context.user_data.clear()
    try:
        zoom = int(update.message.text.strip())
        if zoom < 2 or zoom > 21:
            raise ValueError
    except ValueError:
        update.message.reply_text("Ошибка. Операция остановлена.")
        return ConversationHandler.END
    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
    response = requests.get(geocoder_api_server, params={
        "apikey": APIKEY,
        "format": "json",
        "geocode": geocode
    })
    try:
        toponym = response.json()["response"]["GeoObjectCollection"][
            "featureMember"][0]["GeoObject"]
    except IndexError:
        update.message.reply_text("По вашему запросу ничего не нашлось.")
        return ConversationHandler.END
    toponym_coodrinates = toponym["Point"]["pos"]
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
    ll = ",".join([toponym_longitude, toponym_lattitude])
    request = f"http://static-maps.yandex.ru/1.x/?ll={ll}&z={zoom}&l=map"
    update.message.reply_text("Найдено:")
    context.bot.send_photo(
        update.message.chat_id,
        request
    )
    return ConversationHandler.END


def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", bot_help))
    geo_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("getmap", getmap)],
        states={
            ASKPLC: [MessageHandler(Filters.text, ask_place,
                                    pass_user_data=True)],
            ASKZM: [MessageHandler(Filters.text, ask_zoom,
                                   pass_user_data=True)]
        },
        fallbacks=[CommandHandler('stop', stop,
                                  pass_user_data=True)]
    )

    dp.add_handler(geo_conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()