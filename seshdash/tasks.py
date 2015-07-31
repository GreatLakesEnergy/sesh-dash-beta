from __future__ import absolute_import

from django.conf import settings
from celery import shared_task
from .models import Sesh_Site,PV_Production_Point,Site_Weather_Data

from seshdash.api.enphase import EnphaseAPI
from seshdash.api.forecast import ForecastAPI
from seshdash.api.victron import VictronAPI
from seshdash.utils import time_utils
from datetime import datetime, date, timedelta


"""
Get data related to system voltage, SoC, battery voltage through Victro VRM portal
"""
@shared_task
def get_BOM_data():

    sites = Sesh_Site.objects.all()
    for site in sites:
        v_client = VictronAPI(site.vrm_user_id,site.vrm_password)



@shared_task
def get_enphase_daily_summary(date_range=5):
        #create enphaseAPI
        sites = Sesh_Site.objects.all()
#TODO enphase id needs to go into site object
        en_client = EnphaseAPI(settings.ENPHASE_KEY,settings.ENPHASE_ID)
        #return 'The test task executed with argument "%s" ' % param

        datetime_now = datetime.now()
        datetime_start = datetime_now - timedelta(date_range)
        system_results = {}
        datetime_now_epoch = time_utils.get_epoch_from_datetime(datetime_now)
        datetime_start_epoch = time_utils.get_epoch_from_datetime(datetime_start)
        for site in sites:
                system_results = en_client.get_stats(site.enphase_ID,start=datetime_start_epoch,end=datetime_now_epoch)
                #TODO handle exception of empty result
                print system_results
                for interval in system_results['intervals']:
                #store the data
                    system_pv_data = PV_Production_Point(
                        site = site,
                        time = interval,
                        w_production = interval['enwh'])
                    #system_pv_data.save()
        return "updated enphase data %s"%site

@shared_task
def get_weather_data(days=7,historical=False):
    #TODO figure out way to get weather daya periodicall for forecast of 7 days
    #get all sites
    sites = Sesh_Site.objects.all()
    forecast_result = []
    for site in sites:
        forecast_client = ForecastAPI(settings.FORECAST_KEY,site.latitude,site.longitude)
        if historical:
            #Get weather dates for an extended historical interval
            now = datetime.now()
            days_to_get_from = now - timedelta(days)
            days_arr = time_utils.get_days_interval_delta(days_to_get_from,now)
            forecast_result = forecast_client.get_historical_day_minimal(days_arr)
        else:
            forecast_result = forecast_client.get_n_day_minimal_solar(days)
        #we need to update values in the database
        for day in forecast_result.keys():
            site_weather = Site_Weather_Data.objects.filter(site=site,date=day)
            #if forecast already exists update it
            if site_weather:
                for point in site_weather:
                    point.condition = forecast_result[day]["stat"]
                    point.cloud_cover = forecast_result[day]["cloudcover"]
                    point.save()

            else:
                #else create a new object
                w_data = Site_Weather_Data(
                                site = site,
                                date = day,
                                temp = 0,
                                condition =  forecast_result[day]["stat"],
                                cloud_cover =  forecast_result[day]["cloudcover"],
                                sunrise =  forecast_result[day]["sunrise"],
                                sunset =  forecast_result[day]["sunset"]
                )
                w_data.save()
    return "updated weather for %s"%sites
"""
bulk operation functions
"""
@shared_task
def get_historical_solar(days):
    get_enphase_daily_summary(days)
    get_weather_data(days=days,historical=True)


@shared_task
def get_all_data_initial(days):
    get_weather_data(days)
    get_enphase_daily_summary(days)


