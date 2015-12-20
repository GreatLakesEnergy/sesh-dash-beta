#needed to import some relative libs
from __future__ import absolute_import
import logging

from django.conf import settings
from celery import shared_task
from .models import Sesh_Site,Site_Weather_Data,BoM_Data_Point

#from seshdash.api.enphase import EnphaseAPI
from seshdash.api.forecast import ForecastAPI
from seshdash.api.victron import VictronAPI,VictronHistoricalAPI
from seshdash.utils import time_utils
from seshdash.utils.alert import alert_check
from datetime import datetime, date, timedelta

@shared_task
def get_BOM_data():
    """
    Get data related to system voltage, SoC, battery voltage through Victro VRM portal
    """

    sites = Sesh_Site.objects.all()
    for site in sites:
        print "getting data for site %s "%site
        try:
            v_client = VictronAPI(site.vrm_user_id,site.vrm_password)
            #TODO figure out a way to get these automatically or add
            #them manually to the model for now
            #Also will the user have site's under thier account that they wouldn't like to pull data form?
            #This will throw an error when the objects are getting created
            if v_client.IS_INITIALIZED:
                        bat_data = v_client.get_battery_stats(int(site.vrm_site_id))
                        sys_data = v_client.get_system_stats(int(site.vrm_site_id))
                        date = time_utils.epoch_to_datetime(sys_data['VE.Bus state']['timestamp'] )
                        print bat_data.keys()
                        print sys_data
                        mains = False
                        #check if we have an output voltage on inverter input. Indicitave of if mains on
                        if sys_data['Input voltage phase 1']['valueFloat'] > 0:
                            mains = True



                        data_point = BoM_Data_Point(
                            site = site,
                            time = date,
                            soc = bat_data['Battery State of Charge (System)']['valueFloat'],
                            battery_voltage = bat_data['Battery voltage']['valueFloat'],
                            AC_Voltage_in =  sys_data['Input voltage phase 1']['valueFloat'],
                            AC_Voltage_out = sys_data['Output voltage phase 1']['valueFloat'],
                            AC_input = sys_data['Input power 1']['valueFloat'],
                            AC_output =  sys_data['Output power 1']['valueFloat'],
                            AC_Load_in =  sys_data['Input current phase 1']['valueFloat'],
                            AC_Load_out =  sys_data['Output current phase 1']['valueFloat'],
                            inverter_state = sys_data['VE.Bus state']['nameEnum'],
                            pv_production = sys_data['PV - AC-coupled on output L1']['valueFloat'],
                            #TODO these need to be activated
                            genset_state =  "off",
                            main_on = mains,
                            relay_state = "off",
                            )
                        data_point.save()
                        #TODO get bulk historical data with enphase and weather
                        print "BoM Data saved"
                        # alert if check(data_point) fails
                        alert_check(data_point)
        except IntegrityError, e:
            logging.debug("Duplicate entry skipping data point")
            pass
        except Exception ,e:
            print "error with geting site %s data exception %s"%(site,e)
            logging.exception("error with geting site %s data exception")
            pass


@shared_task
def get_historical_BoM(date_range=5):
        """
        Get Historical Data from VRM to backfill any days
        """
        datetime_now = datetime.now()
        datetime_start = datetime_now - timedelta(date_range)

        datetime_now_epoch = time_utils.get_epoch_from_datetime(datetime_now)
        datetime_start_epoch = time_utils.get_epoch_from_datetime(datetime_start)

        sites = Sesh_Site.objects.all()
        count = 0
        for site in sites:
            v_client = VictronAPI(site.vrm_user_id,site.vrm_password)
            vh_client = VictronHistoricalAPI(site.vrm_user_id,site.vrm_password)
            site_id = site.vrm_site_id
            for site_id in v_client.SYSTEMS_IDS:
                #site_id is a tuple
                data = vh_client.get_data(site_id[0],datetime_start_epoch,datetime_now_epoch)
                for row in data:
                    data_point = BoM_Data_Point(
                        site = site,
                        time = row['Date Time'],
                        soc = row['Battery State of Charge (System)'],
                        battery_voltage = row['Battery voltage'],
                        AC_input = row['Input power 1'],
                        AC_output =  row['Output power 1'],
                        AC_Load_in =  row['Input current phase 1'],
                        AC_Load_out =  row['Output current phase 1'],
                        inverter_state = row['VE.Bus Error'],
                        #TODO these need to be activated
                        genset_state =  "off",
                        relay_state = "off",
                        )
                    data_point.save()
                    count = count +1
            print "saved %s BoM data points"%count


@shared_task
def get_enphase_daily_summary(date=None):
        calc_range = timedelta(hours = 24)
        if not date:
            date = datetime.now()

        sites = Sesh_Site.objects.all()

        for site in sites:
                 en_client = EnphaseAPI(settings.ENPHASE_KEY,site.enphase_ID)
                 system_id = site.enphase_site_id

                 end_time_str = en_client.SYSTEMS_INFO[system_id]['summary_date']
                 system_pv_data = PV_Production_Point(
                     site = site,
                     time = end_time_str,
                     wh_production = en_client.SYSTEMS_INFO[system_id]['energy_today'],
                     #TODO this is not alwyas there when we are tlking about aggrearegate data needs to be resolved
                     w_production = en_client.SYSTEMS_INFO[system_id]['current_power'],
                     data_duration = calc_range
                    )
                 system_pv_data.save()


@shared_task
def get_enphase_daily_stats(date=None):
        """
        Get enphase daily data or get aggregate data
        """
        calc_range = timedelta(minutes=15)

        #create enphaseAPI
        sites = Sesh_Site.objects.all()

        #return 'The test task executed with argument "%s" ' % param
        #get dates we want to get
        datetime_now = datetime.now()
        datetime_start = datetime_now - timedelta(days=1)
        system_results = {}

        if date:
            datetime_now = date
            datetime_start = datetime_now - timedelta(days=1)


        #turn them into epoch seconds
        datetime_start_epoch = time_utils.get_epoch_from_datetime(datetime_start)
        for site in sites:
                en_client = EnphaseAPI(settings.ENPHASE_KEY,site.enphase_ID)
                system_id = site.enphase_site_id
                print "gettig stats for %s"%system_id
                system_results = en_client.get_stats(system_id,start=datetime_start_epoch)

                #TODO handle exception of empty result
                print len(system_results['intervals'])
                for interval in system_results['intervals']:
                        #store the data
                        print interval
                        end_time_str = time_utils.epoch_to_datetime(interval['end_at'])
                        system_pv_data = PV_Production_Point(
                            site = site,
                            time = end_time_str,
                            wh_production = interval['enwh'],
                            w_production = interval['powr'],
                            #TODO time interval shouldn't be static this needs to be calculated based on data returned,
                            data_duration = calc_range
                            )
                        system_pv_data.save()
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
@shared_task
def get_historical_solar(days):
    """
    bulk operation functions
    """
    get_enphase_daily_summary(days)
    get_weather_data(days=days,historical=True)


@shared_task
def get_all_data_initial(days):
    get_weather_data(days)
    get_enphase_daily_summary(days)
