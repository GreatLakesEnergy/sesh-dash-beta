#needed to import some relative libs
from __future__ import absolute_import
import logging

from django.conf import settings
from django.db import IntegrityError
from django.forms.models import model_to_dict
from celery import shared_task
from .models import Sesh_Site,Site_Weather_Data,BoM_Data_Point,Daily_Data_Point,Sesh_Alert

#from seshdash.api.enphase import EnphaseAPI
from seshdash.api.forecast import ForecastAPI
from seshdash.api.victron import VictronAPI,VictronHistoricalAPI
from seshdash.utils import time_utils
from seshdash.utils.alert import alert_check
from seshdash.data.db.influx import Influx

from datetime import datetime, date, timedelta

def send_to_influx(model_data, site, timestamp, to_exclude=[]):
    """
    Utility function to send data to influx
    """

    i = Influx()
    model_data_dict = model_to_dict(model_data)

    if to_exclude:
        # Remove any value we wish not to be submitted
        # Generally used with datetime measurement
        for val in to_exclude:
            #if to_exclude  in model_data_dict.keys():
            model_data_dict.pop(val)

    i.send_object_measurements(model_data_dict, timestamp=timestamp, tags={"site_id":site.id, "site_name":site.site_name})


@shared_task
def get_BOM_data():
    """
    Get data related to system voltage, SoC, battery voltage through Victro VRM portal
    """

    sites = Sesh_Site.objects.all()
    for site in sites:
        print "getting data for site %s "%site
        try:
            v_client = VictronAPI(site.vrm_account.vrm_user_id,site.vrm_account.vrm_password)
            #TODO figure out a way to get these automatically or add
            #them manually to the model for now
            #Also will the user have site's under thier account that they wouldn't like to pull data form?
            #This will throw an error when the objects are getting created
            if v_client.IS_INITIALIZED:
                        bat_data = v_client.get_battery_stats(int(site.vrm_site_id))
                        sys_data = v_client.get_system_stats(int(site.vrm_site_id))
                        date = time_utils.epoch_to_datetime(sys_data['VE.Bus state']['timestamp'] )
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
                            AC_output_absolute =  float(sys_data['Output power 1']['valueFloat']) +
                                                    float(sys_data['PV - AC-coupled on output L1']['valueFloat']),
                            AC_Load_in =  sys_data['Input current phase 1']['valueFloat'],
                            AC_Load_out =  sys_data['Output current phase 1']['valueFloat'],
                            inverter_state = sys_data['VE.Bus state']['nameEnum'],
                            pv_production = sys_data['PV - AC-coupled on output L1']['valueFloat'],
                            #TODO these need to be activated
                            genset_state =  0,
                            main_on = mains,
                            relay_state = 0,
                            )
                        data_point.save()
                        # Send to influx
                        send_to_influx(data_point, site, date, to_exclude=['time'])

                        print "BoM Data saved"
                        # Alert if check(data_point) fails
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
    i = Influx()
    sites = Sesh_Site.objects.all()
    forecast_result = []

    for site in sites:
        forecast_client = ForecastAPI(settings.FORECAST_KEY,site.position.latitude,site.position.longitude)
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
                send_to_influx(site, w_data, date, to_exclude=['date'])

    return "updated weather for %s"%sites



def find_chunks(input_list,key):
    """
    Find consecutive chunks in list
    will return a list comprimised of dictionaries [{value:number_of_interval},..]
    """
    result_list = []
    section = {}
    count = 0
    for i in xrange(0,len(input_list)-1):
        if count > 0:
            section[input_list[i][key]] = count
        if input_list[i][key] == input_list[i+1][key]:
            count = count + 1
            if i == (len(input_list)-2):
            # We are at end of list
                result_list.append(section)
        else:
            count = 0
            section = {}
            result_list.append(section)

    return result_list


def get_grid_stats(measurement_dict_list, measurement_value, measurement_key, bucket_size):
    """
    Utility tool that will calculate time delta for consecutive measurements
    if a measurement is happens to be 0 X times this will find the duration
    """
    time_gap = bucket_size #TODO this should be a global defined by celery job runtime
    result_dict = {}
    chunked_list = find_chunks(measurement_dict_list,measurement_key)
    logging.debug("Chunked list  %s"%chunked_list)
    count = 0
    for chunk_dict in chunked_list:
        if measurement_value in chunk_dict.keys():
            result_dict['duration'] = time_gap * chunk_dict[measurement_value]
            result_dict['count'] = count + 1
    logging.debug("Found chunks %s"%result_dict)
    return result_dict


def get_aggregate_data(site, measurement, delta='24h', bucket_size='1h', clause=None, toSum=True):
    """
    Calucalte aggregate values from Influx for provided measuruements
    """
    i = Influx()
    result = 0
    operator = 'mean'

    clause_opts = {
            'negative': (lambda x : x[operator] < 0),
            'positive' : (lambda x: x[operator] > 0 ),
            'zero' : (lambda x: x[operator] == 0)}

    if clause and not clause in clause_opts.keys():
        logging.error("unkown clause provided %s allowed %s"%(clause,clause_opts.keys()))
        return 0

    #get measurement values from influx
    if not toSum:
        operator = 'min'

    aggr_results = i.get_measurement_bucket(measurement, bucket_size, 'site_name', site.site_name, delta, operator=operator)

    #logging.debug("influx results %s "%(aggr_results))

    #we have mean values by the hour now aggregate them
    if aggr_results:
        agr_value = []
        if clause:
            #if we have a cluase filter to apply
            aggr_results = filter(clause_opts[clause],aggr_results)

        if toSum:
            agr_value.append(sum(map(lambda x: x[operator], aggr_results)))
            resuls = agr_value
        else:
            result = aggr_results


        logging.debug("Aggregateing %s %s agr:%s"%(measurement,aggr_results,agr_value))
    else:
        logging.warning("No Values returned for aggregate. Check Influx Connection.")
    return result


@shared_task
def get_aggregate_daily_data():
    """
    Batch job to get daily aggregate data for each site
    """
    sites  = Sesh_Site.objects.all()
    print "Aggregating daily consumption and production stats"
    for site in sites:
            yesterday = time_utils.get_yesterday()

            logging.debug("aggregate data for %s"%site)
            aggregate_data_pv = get_aggregate_data (site, 'pv_production')
            aggregate_data_AC = get_aggregate_data (site, 'AC_output_absolute')
            aggregate_data_batt = get_aggregate_data (site, 'AC_output', clause='negative')
            aggregate_data_grid = get_aggregate_data (site, 'AC_input', clause='positive')
            aggregate_data_grid_data = get_aggregate_data (site, 'AC_Voltage_in',bucket_size='10m', toSum=False)

            logging.debug("aggregate date for grid %s "%aggregate_data_grid_data)
            aggregate_data_grid_outage_stats = get_grid_stats(aggregate_data_grid_data, 0, 'min',10)
            aggregate_data_alerts = Sesh_Alert.objects.filter(site=site, date=yesterday)
            sum_power_pv = aggregate_data_AC - aggregate_data_grid



            # Create model of aggregates
            daily_aggr = Daily_Data_Point(
                                         site = site,
                                         daily_pv_yield = aggregate_data_pv,
                                         daily_power_consumption_total = aggregate_data_AC,
                                         daily_battery_charge = aggregate_data_batt,
                                         daily_power_cons_pv = sum_power_pv,
                                         daily_grid_usage = aggregate_data_grid,
                                         daily_grid_outage_t = aggregate_data_grid_outage_stats['duration'],
                                         daily_grid_outage_n = aggregate_data_grid_outage_stats['count'],
                                         daily_no_of_alerts = aggregate_data_alerts.count(),
                                         date = yesterday,
                                            )

            daily_aggr.save()
            #send to influx
            send_to_influx(daily_aggr, site, time_utils.get_yesterday(), to_exclude=['date'])



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
