from telegram.ext import ConversationHandler, CommandHandler, MessageHandler
from telegram.ext import Filters
from funks.functions import get_ll
from tgfunks.basefunks import stop, STOP_KEYBOARD, BASE_KEYBOARD


class InvalidZoom(Exception):
    pass


ASKZOOM, ASKPLACE = range(2)


def getmap(update, context):
    update.message.reply_text("Введите искомый адрес.",
                              reply_markup=STOP_KEYBOARD)
    return ASKPLACE


def ask_place(update, context):
    plc = update.message.text
    if plc.strip() == '/stop':
        stop(update, context)
    else:
        if not get_ll(plc):
            update.message.reply_text("По вашему запросу ничего не нашлось...")
            update.message.reply_text("Введите команду /stop или искомый адрес.")
            return ASKPLACE
        context.user_data['place'] = plc
    update.message.reply_text("Задайте параметр приближения " +
                              "(целое цисло от 2 до 21).")
    return ASKZOOM


def ask_zoom(update, context):
    geocode = context.user_data['place']
    context.user_data.clear()
    try:
        zoom = int(update.message.text.strip())
        if zoom < 2 or zoom > 21:
            raise InvalidZoom
    except InvalidZoom as e:
        update.message.reply_text("Ошибка: InvalidZoom")
        update.message.reply_text("Введите команду /stop или искомый адрес.")
        return ASKPLACE
    ll = get_ll(geocode)
    request = f"http://static-maps.yandex.ru/1.x/?ll={ll}&z={zoom}&l=map"
    update.message.reply_text("Найдено!")
    context.bot.send_photo(
        update.message.chat_id,
        request
    )
    update.message.reply_text("Введите команду /stop искомый адрес.")
    return ASKPLACE


geo_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("getmap", getmap)],
    states={
        ASKPLACE: [MessageHandler(Filters.text & ~Filters.command, ask_place,
                                  pass_user_data=True)],
        ASKZOOM: [MessageHandler(Filters.text & ~Filters.command, ask_zoom,
                                 pass_user_data=True)]
    },
    fallbacks=[CommandHandler('stop', stop,
                              pass_user_data=True)]
)