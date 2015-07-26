import requests json

class Wunnderground():
    API_BASE_URL = " http://api.wunderground.com/api/{key}/{features}/{settings}/q/{query}.{format}"
    KEY = ""
    FORMAT = ""

    def __init__(self,key, format_type=json):
        self.KEY = key
        self.FORMAT =  format_type


