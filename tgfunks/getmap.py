from telegram.ext import ConversationHandler, CommandHandler, MessageHandler
from telegram.ext import Filters
from funks.functions import get_ll
from tgfunks.basefunks import stop


ASKZOOM, ASKPLACE = range(2)


def getmap(update, context):
    update.message.reply_text("Введите искомый адрес.")
    return ASKPLACE


def ask_place(update, context):
    context.user_data['place'] = update.message.text
    update.message.reply_text("Задайте параметр приближения " +
                              "(целое цисло от 2 до 21).")
    return ASKZOOM


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
    if get_ll(geocode):
        ll = get_ll(geocode)
    else:
        update.message.reply_text("Ошибка. Операция остановлена.")
        return ConversationHandler.END
    request = f"http://static-maps.yandex.ru/1.x/?ll={ll}&z={zoom}&l=map"
    update.message.reply_text("Найдено:")
    context.bot.send_photo(
        update.message.chat_id,
        request
    )
    return ConversationHandler.END


geo_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("getmap", getmap)],
    states={
        ASKPLACE: [MessageHandler(Filters.text, ask_place,
                                  pass_user_data=True)],
        ASKZOOM: [MessageHandler(Filters.text, ask_zoom,
                                 pass_user_data=True)]
    },
    fallbacks=[CommandHandler('stop', stop,
                              pass_user_data=True)]
)