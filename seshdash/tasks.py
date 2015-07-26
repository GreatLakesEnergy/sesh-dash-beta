from __future__ import absolute_import

from django.conf import settings
from celery import shared_task
from .models import Sesh_Site,PV_Production_Point,Site_Weather_Data

from seshdash.api.enphase import EnphaseAPI
from seshdash.api.forecast import ForecastAPI
from seshdash.api.victron import VictronAPI
from seshdash.utils import time_utils
from datetime import datetime, date, timedelta


#We need to pre populate enphase data in the DB
@shared_task
def get_enphase_daily_summary(date_range=5):
        #create enphaseAPI
        sites = Sesh_Site.objects.all()
        en_client = EnphaseAPI(settings.ENPHASE_KEY,settings.ENPHASE_ID)
        #return 'The test task executed with argument "%s" ' % param

        datetime_now = datetime.now()
        datetime_yesterday = datetime_now - timedelta(date_range)
        system_results = {}
        for site in sites:
            for day in xrange(0,date_range):
                date_to_get = datetime_now - timedelta(day)
                #formate date to yyyy-MM-DD so enphase likes it
                formated_date = date_to_get.strftime("%Y-%m-%d")
                #TODO add enphase system ID to site MODEL HARCODING NOW
                system_results = en_client.get_summary('546698',summary_date=formated_date)
                print system_results

                #store the data
                system_pv_data = PV_Production_Point(
                        site = site,
                        time = date_to_get,
                        w_production = system_results['energy_today'])
                system_pv_data.save()
        return "updated enphase data %s"%site

@shared_task
def get_weather_data():
    #TODO figure out way to get weather daya periodicall for forecast of 7 days
    #get all sites
    sites = Sesh_Site.objects.all()
    for site in sites:
        forecast_client = ForecastAPI(settings.FORECAST_KEY,site.latitude,site.longitude)
        forecast_result = forecast_client.get_n_day_minimal_solar(7)
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
                #else create a new objecr
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
Get data related to system voltage, SoC, battery voltage through Victro VRM portal
"""
@shared_task
def get_BOM_data():

    sites = Sesh_Site.objects.all()

    [[[
