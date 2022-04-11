import logging
from telegram.ext import Updater
from telegram.ext import CommandHandler
import urllib3
from tgfunks.getmap import geo_conv_handler
from tgfunks.getweather import weather_conv_handler
from tgfunks.basefunks import *


logging.basicConfig(filename='other/telegram_bot.log',
                    filemode='w',
                    format='%(asctime)s - %(name)s -'
                           '%(levelname)s - %(message)s',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TOKEN = ""


def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", bot_help))
    dp.add_handler(geo_conv_handler)
    dp.add_handler(weather_conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()