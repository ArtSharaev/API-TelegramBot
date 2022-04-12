from telegram.ext import ConversationHandler, CommandHandler, MessageHandler
from telegram.ext import Filters
from funks.functions import get_ll, get_address_from_ll
from tgfunks.basefunks import stop, STOP_KEYBOARD
import requests
import pymorphy2

MORPH = pymorphy2.MorphAnalyzer()
ASKCITY = range(1)
WEATHER_APIKEY = ""


def getweather(update, context):
    update.message.reply_text('Для какого города вы хотите узнать погоду?',
                              reply_markup=STOP_KEYBOARD)
    return ASKCITY


def ask_city(update, context):
    geocode = update.message.text
    if geocode.strip() == '/stop':
        stop(update, context)
    geocode = update.message.text
    if get_ll(geocode):
        ll = get_ll(geocode).split(',')
    else:
        update.message.reply_text("По вашему запросу ничего не нашлось...")
        update.message.reply_text("Введите команду /stop или город.")
        return ASKCITY
    url_yandex = f'https://api.weather.yandex.ru/v2/forecast/?lat={ll[1]}&lon={ll[0]}&[lang=ru_RU]'
    response = requests.get(url_yandex, headers={'X-Yandex-API-Key': WEATHER_APIKEY}, verify=False)
    conditions = {'clear': 'ясно', 'partly-cloudy': 'малооблачно', 'cloudy': 'облачно с прояснениями',
                  'overcast': 'пасмурно', 'drizzle': 'морось', 'light-rain': 'небольшой дождь',
                  'rain': 'дождь', 'moderate-rain': 'умеренно сильный', 'heavy-rain': 'сильный дождь',
                  'continuous-heavy-rain': 'длительный сильный дождь', 'showers': 'ливень',
                  'wet-snow': 'дождь со снегом', 'light-snow': 'небольшой снег', 'snow': 'снег',
                  'snow-showers': 'снегопад', 'hail': 'град', 'thunderstorm': 'гроза',
                  'thunderstorm-with-rain': 'дождь с грозой', 'thunderstorm-with-hail': 'гроза с градом'
                  }
    wind_dir = {'nw': 'северо-западное', 'n': 'северное', 'ne': 'северо-восточное', 'e': 'восточное',
                'se': 'юго-восточное', 's': 'южное', 'sw': 'юго-западное', 'w': 'западное', 'c': 'штиль'}
    yandex_json = response.json()
    fact_dict = yandex_json['fact']
    if fact_dict['is_thunder']:
        th = ', гроза'
    else:
        th = ''
    try:
        address = get_address_from_ll(get_ll(geocode)).split(', ')
        address = ", ".join(address[:-2])
    except IndexError:
        update.message.reply_text("Введенное не является городом или населенным пунктом.")
        update.message.reply_text("Введите команду /stop или город.")
        return ASKCITY
    w = f"""
    Погода по адресу:
    
  {address}
    
    •   {conditions[fact_dict['condition']].capitalize()}{th}
    
    •   {str(fact_dict['temp'])} ℃, ощущается как {str(fact_dict['feels_like'])} ℃
    
    •   {MORPH.parse(wind_dir[fact_dict['wind_dir']])[0].inflect({'masc', 'sing'}).word.capitalize()} ветер {str(fact_dict['wind_speed'])} м/с

    •   Давление {str(fact_dict['pressure_mm'])} мм рт. ст.
    
    •   Влажность {str(fact_dict['humidity'])}%
    """
    update.message.reply_text(w)
    update.message.reply_text("Введите команду /stop или город.")
    return ASKCITY


weather_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("getweather", getweather)],
    states={
        ASKCITY: [MessageHandler(Filters.text & ~Filters.command, ask_city)]
    },
    fallbacks=[CommandHandler('stop', stop)]
)