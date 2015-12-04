import forecastio

class ForecastAPI:

    _API_KEY = "8eefab4d187a39b993ca9c875fef6159"
    _LAZY = False
    _LAT = 0
    _LNG = 0

    _forecast = ()

    def __init__(self,key,lat,lng,lazy=False):
        self._LAT = lat
        self._LNG = lng
        self._API_KEY = key
        self._LAZY = lazy
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
    Helper on getting cloud sunrise and sunset data from the past
    """
    def get_historical_day_minimal_solar(self,days):
        #TODO get temp just for reference
        sun_results = {}
        for day in days:
            print "getting date for %s"%day
            self._forecast = forecastio.load_forecast(self._API_KEY,self._LAT,self._LNG,lazy=self._LAZY,time=day)
            c_data = self._forecast.daily().data
            for f_day in c_data:
                print "adding date for %s"%f_day
                sun_results[day.isoformat()] = {"sunrise":f_day.sunriseTime,"sunset":f_day.sunsetTime,"stat":f_day.icon,"cloudcover":f_day.cloudCover}

        return sun_results



