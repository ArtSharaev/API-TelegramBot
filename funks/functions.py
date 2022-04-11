import requests

MAPS_APIKEY = ""


def get_ll(geocode):
    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
    response = requests.get(geocoder_api_server, params={
        "apikey": MAPS_APIKEY,
        "format": "json",
        "geocode": geocode
    })
    try:
        toponym = response.json()["response"]["GeoObjectCollection"][
            "featureMember"][0]["GeoObject"]
    except IndexError:
        return None
    toponym_coodrinates = toponym["Point"]["pos"]
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
    ll = ",".join([toponym_longitude, toponym_lattitude])
    return ll
