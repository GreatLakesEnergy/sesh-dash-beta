import forecastio

class ForecastAPI:

    _API_KEY = "8eefab4d187a39b993ca9c875fef6159"

    _LAT = 0
    _LNG = 0

    _forecast = ()

    def __init__(self,key,lat,lng,lazy=False):
        self._LAT = lat
        self._LNG = lng
        self._API_KEY = key
        self._forecast = forecastio.load_forecast(self._API_KEY,self._LAT,self._LNG,lazy=lazy)

    def get_7day_forecast_detailed(self):
            return self._forecast.daily().data

    """
    Help getting cloud data from the future
    """
    def get_7_day_cloudCover(self):

        c_data = self._forecast.daily().data
        cloud_results = {}
        for day in c_data:
            cloud_results[day.time.isoformat()] = day.cloudCover

        return cloud_results


    """
    Helper on getting cloud sunrise and sunset data
    """
    def get_n_day_minimal_solar(self,n_days):

        c_data = self._forecast.daily().data
        sun_results = {}
        count = 0
        for day in c_data:
            if count < n_days:
                sun_results[day.time.isoformat()] = {"sunrise":day.sunriseTime,"sunset":day.sunsetTime,"stat":day.icon,"cloudcover":day.cloudCover}
                count = count + 1

        return sun_results

    """
    Helper on getting cloud sunrise and sunset data
    """
    def get_historical_day_minimal_solar(self,date):
        #TODO get temp just for reference
        self._forecast = forecastio.load_forecast(self._API_KEY,self._LAT,self._LNG,lazy=lazy,time=date)
        c_data = self._forecast.daily().data
        sun_results = {}
        for day in c_data:
            sun_results[day.time.isoformat()] = {"sunrise":day.sunriseTime,"sunset":day.sunsetTime,"stat":day.icon,"cloudcover":day.cloudCover}

        return sun_results



