# Needed to import some relative libs
from __future__ import absolute_import
import logging
import sys
import pytz

from django.conf import settings
from django.db import IntegrityError,transaction
from django.forms.models import model_to_dict
from celery import shared_task,states
from celery.signals import task_failure,task_success
from .models import Sesh_Site,Site_Weather_Data,BoM_Data_Point,Daily_Data_Point,Sesh_Alert,Alert_Rule, RMC_status, Sesh_RMC_Account, Data_Process_Rule

#fraom seshdash.api.enphase import EnphaseAPI
from seshdash.api.forecast import ForecastAPI
from seshdash.api.victron import VictronAPI,VictronHistoricalAPI
from seshdash.utils.alert import alert_generator, alert_status_check
from seshdash.utils.reporting import prepare_report
from seshdash.data.db.influx import Influx, get_latest_point_site

# Time related
from datetime import datetime, date, timedelta
from dateutil.parser import parse
from seshdash.utils import time_utils
from django.utils import timezone

logger = logging.getLogger(__name__)

@task_failure.connect
def handle_task_failure(**kw):
    message = 'error occured in task: %s message: %s'%(kw.get('name','name not defined'),kw.get('message','no message'))
    logger.error("CELERY TASK FAILURE:%s"%(message))
    if not settings.DEBUG:
        import rollbar
        rollbar.report_exc_info(message=message,extra_data=kw)


def send_to_influx(model_data, site, timestamp, to_exclude=[],client=None, send_status=True):
    """
    Utility function to send data to influx
    """
    try:
        if client:
            i = client
        else:
            i = Influx()

        model_data_dict = model_to_dict(model_data)

        if to_exclude:
            # Remove any value we wish not to be submitted
            # Generally used with datetime measurement
            for val in to_exclude:
                #if to_exclude  in model_data_dict.keys():
                model_data_dict.pop(val)

        #Add our status will be used for RMC_Status
        if send_status:
            model_data_dict['status'] = 1.0

        status = i.send_object_measurements(model_data_dict, timestamp=timestamp, tags={"site_id":site.id, "site_name":site.site_name})
    except Exception,e:
        message = "Error sending to influx with exception %s in datapint %s"%(e,model_data_dict)
        handle_task_failure(message= message, name='send_to_influx' ,exception=e,data=model_data)

def generate_auto_rules(site_id):
    """
    Generate standard rules when a siteis created
    """
    site = Sesh_Site.objects.get(pk=site_id)

    logger.info("Running auto rule generation")
    # Create battery low voltage alarm
    lv_alarm = Alert_Rule(site =site,
                        check_field = 'BoM_Data_Point#battery_voltage',
                        value = site.system_voltage,
                        operator = 'lt',
            )

    # Create soc low voltage alarm
    soc_alarm = Alert_Rule(site =site,
                        check_field = 'BoM_Data_Point#soc',
                        value = 35,
                        operator = 'lt',
            )
    # Create communication alarm
    com_alarm = Alert_Rule(site =site,
                        check_field = 'RMC_status#minutes_last_contact',
                        value = 60,
                        operator = 'gt',
            )

    lv_alarm.save()
    com_alarm.save()
    soc_alarm.save()

    logger.debug("Added low voltage, soc, and comm alert for site %s"%site)


@shared_task
def get_BOM_data():
    # Get all sites that have vrm id
    sites = Sesh_Site.objects.exclude(vrm_site_id__isnull=True).exclude(vrm_site_id__exact='')
    logger.info("Running VRM data collection")
    for site in sites:
        logger.debug("Getting VRM data for %s"%site)
        try:
            v_client = VictronAPI(site.vrm_account.vrm_user_id,site.vrm_account.vrm_password)

            if v_client.IS_INITIALIZED:
                        bat_data = v_client.get_battery_stats(int(site.vrm_site_id))
                        sys_data = v_client.get_system_stats(int(site.vrm_site_id))
                        #This data is already localazied
                        logger.debug("got raw date %s with timezone %s"%(
                            sys_data['VE.Bus state']['timestamp'],
                            site.time_zone
                            ))
                        date = time_utils.epoch_to_datetime(float(sys_data['VE.Bus state']['timestamp']) , tz=site.time_zone)
                        #logger.debug("saving before localize  BOM data point with time %s"%date)
                        logger.debug("saving BOM data point with time %s"%date)
                        mains = False
                        #check if we have an output voltage on inverter input. Indicitave of if mains on
                        if sys_data['Input voltage phase 1']['valueFloat'] > 0:
                            mains = True

                        data_point = BoM_Data_Point(
                            site = site,
                            time = date,
                            soc = bat_data.get('Battery State of Charge (System)',{}).get('valueFloat',0),
                            battery_voltage = bat_data.get('Battery voltage',{}).get('valueFloat',0),
                            AC_Voltage_in =  sys_data['Input voltage phase 1']['valueFloat'],
                            AC_Voltage_out = sys_data['Output voltage phase 1']['valueFloat'],
                            AC_input = sys_data['Input power 1']['valueFloat'],
                            AC_output =  sys_data['Output power 1']['valueFloat'],
                            AC_output_absolute =  float(sys_data['Output power 1']['valueFloat']) +
                                                    float(sys_data.get('PV - AC-coupled on output L1',{}).get('valueFloat',0)),
                            AC_Load_in =  sys_data['Input current phase 1']['valueFloat'],
                            AC_Load_out =  sys_data['Output current phase 1']['valueFloat'],
                            inverter_state = sys_data['VE.Bus state']['nameEnum'],
                            pv_production = sys_data.get('PV - AC-coupled on output L1',{}).get('valueFloat',0),
                            #TODO these need to be activated
                            genset_state =  0,
                            main_on = mains,
                            relay_state = 0,
                            )
                	with transaction.atomic():
                        	data_point.save()
                        # Send to influx
                        send_to_influx(data_point, site, date, to_exclude=['time'])

                        # Alert if check(data_point) fails

        except IntegrityError, e:
            logger.debug("Duplicate entry skipping data point")
            pass
        except KeyError,  e:
            logger.warning("Sites %s is missing key while getting vrm data%s"%(site,e))
        except Exception ,e:
            message = "error with geting site %s data exception %s"%(site,e)
            logger.exception("error with geting site %s data exception"%site)
            handle_task_failure(message = message, exception=e, name='get_BOM_data' )
            pass


def _check_data_pont(data_point_arr):
        """
        Check whether our dp is valid return tru if it is false otherwise
        """
        # Return False if any of the valuse are empty
        return filter(lambda x: x==True, map(lambda x: data_point_arr[x].strip()=='',data_point_arr))

@shared_task
def get_historical_BoM(site_pk,start_at):
        """
        Get Historical Data from VRM to backfill any days
        """
        i = Influx()
        count = 0
        site = Sesh_Site.objects.get(pk=site_pk)
        site_id = site.vrm_site_id
        if not site_id:
            logger.info("skipping site %s has not vrm_site_id"%site)
            return 0
        vh_client = VictronHistoricalAPI(site.vrm_account.vrm_user_id,site.vrm_account.vrm_password)
        #site_id is a tuple
        #print "getting data for siteid %s starting at %s"%(site.vrm_site_id,start_at)
        data = vh_client.get_data(site_id,start_at)
        logger.debug("Importing data for site:%s"%site)
        for row in data:
            try:
                parsed_date = datetime.strptime(row.get('Date Time'),'%Y-%m-%d %X')
                date = time_utils.localize(parsed_date, tz=site.time_zone)
                data_point = BoM_Data_Point(
                    site = site,
                    time = date,
                    soc = row.get('Battery State of Charge (System)', 0),
                    battery_voltage = row.get('Battery voltage', 0),
                    AC_input = row.get('Input power 1', 0),
                    AC_output =  row.get('Output power 1', 0),
                    AC_Load_in =  row.get('Input current phase 1', 0),
                    AC_Load_out =  row.get('Output current phase 1', 0),
                    inverter_state = row.get('VE.Bus Error', ''),
                    pv_production = row.get('PV - AC-coupled on input L1', 0), # IF null need to put in 0
                    #TODO these need to be activated
                    genset_state =  0,
                    relay_state = 0,
                    )
                date =  row.get('Date Time')

                with transaction.atomic():
                    data_point.save()
                send_to_influx(data_point, site, date, to_exclude=['time','inverter_state','id'],client=i, send_status=False)

                count = count +1
                if count % 100:
                    logger.debug("imported  %s points"%count)
                #print "saved %s BoM data points"%count
            except IntegrityError, e:
                    logger.warning("data point already exist %s"%e)
                    pass
            except ValueError,e:
                    logger.warning("Invalid values in data point dropping  %s"%(e))
                    pass
            except Exception,e:
                    message = "error with creating data point  data exception %s"%(e)
                    logger.debug(message)
                    logger.exception( message )
                    handle_task_failure(message = message, name= 'get_Hitorical_bom')
                    pass

        logger.debug("saved %s BoM data points"%count)
        # Clean up
        site.import_data  = False
        site.save()
        vh_client.flush()

        # Return number of items found
        return count

@shared_task
def run_aggregate_on_historical(site_id):
    """
    this will run daily aggregation caluclations for each each day
    """
    site = Sesh_Site.objects.get(pk=site_id)
    start_date = site.comission_date # TODO this hould porbably be based on range in DB
    end_date =  timezone.localtime(timezone.now())
    days_to_agr = time_utils.get_time_interval_array(24,'hours',start_date,end_date)
    logger.debug( "getting historic aggregates %s"%(days_to_agr))
    for day in days_to_agr:
        logger.debug("Batch processing aggregates")
        get_aggregate_daily_data(day)

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
        #get dates we want to get default this is last 24 hours
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
                #print "gettig stats for %s"%system_id
                system_results = en_client.get_stats(system_id,start=datetime_start_epoch)

                #TODO handle exception of empty result
                #print len(system_results['intervals'])
                for interval in system_results['intervals']:
                        #store the data
                        #print interval
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

                    send_to_influx(point, site, day, to_exclude=['date'], send_status=False)

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
                send_to_influx(w_data, site, day, to_exclude=['date'], send_status=False)

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
    result_dict = {
                    'duration':0,
                    'count':0
                }

    chunked_list = find_chunks(measurement_dict_list,measurement_key)
    logger.debug("Chunked list  %s"%chunked_list)
    count = 0
    for chunk_dict in chunked_list:
        if measurement_value in chunk_dict.keys():
            result_dict['duration'] = time_gap * chunk_dict[measurement_value]
            result_dict['count'] = count + 1
    logger.debug("Found chunks %s"%result_dict)
    return result_dict


def get_aggregate_data(site, measurement, bucket_size='1h', clause=None, toSum=True, operator='mean', start='now'):
    """
    Calculate aggregate values from Influx for provided measuruements
    """
    i = Influx()
    result = [0]

    clause_opts = {
            'negative': (lambda x : x[operator] < 0),
            'positive' : (lambda x: x[operator] > 0 ),
            'zero' : (lambda x: x[operator] == 0)}

    if clause and not clause in clause_opts.keys():
        logger.error("unkown clause provided %s allowed %s"%(clause,clause_opts.keys()))
        return result

    #get measurement values from influx
    if not toSum:
        operator = 'min'

    aggr_results = i.get_measurement_bucket(measurement, bucket_size, 'site_name', site.site_name, operator=operator, start=start)

    logger.debug("influx results %s "%(aggr_results))

    #we have mean values by the hour now aggregate them
    if aggr_results:
        agr_value = []
        if clause:
            #if we have a cluase filter to apply
            aggr_results = filter(clause_opts[clause],aggr_results)

        if toSum:
            to_sum_vals = map (lambda x: x[operator], aggr_results)
            agr_value.append(sum(to_sum_vals))
            result = agr_value
        else:
            result = aggr_results

        logger.debug("Aggregating %s %s agr:%s"%(measurement,aggr_results,agr_value))
    else:
        message = "No Values returned for aggregate. Check Influx Connection."
        logger.warning(message)

    return result


@shared_task
def get_aggregate_daily_data(date=None):
    """
    Batch job to get daily aggregate data for each sites,
    Data_Process_Rule will be used to determine how the aggreation function should be applied

    @params date - datetime object to do aggregations on
    """
    sites  = Sesh_Site.objects.all()
    date_to_fetch = time_utils.get_yesterday()

    if date:
        date_to_fetch =  date

    for site in sites:
            site_rules = Data_Process_Rule.objects.filter(site=site)

            logger.debug("aggregate data for %s date: %ss"%(site,date_to_fetch))
            agg_dict = {}

            for rule in site_rules:
                result = get_aggregate_data(site,
                        rule.input_field.field_name,
                        start=date_to_fetch,
                        operator=rule.function


            """
            agg_dict['aggregate_data_pv'] = get_aggregate_data (site, 'pv_production',start=date_to_fetch)[0]
            agg_dict['aggregate_data_AC'] = get_aggregate_data (site, 'AC_output_absolute',start=date_to_fetch)[0]
            agg_dict['aggregate_data_batt'] = get_aggregate_data (site, 'AC_output', clause='negative', start=date_to_fetch)[0]
            agg_dict['aggregate_data_grid'] = get_aggregate_data (site, 'AC_input', clause='positive',start=date_to_fetch)[0]
            agg_dict['aggregate_data_grid_data'] = get_aggregate_data (site, 'AC_Voltage_in',bucket_size='10m', toSum=False, start=date_to_fetch)

            # Calculate outage data
            logger.debug("aggregate date for grid %s "%agg_dict['aggregate_data_grid_data'])
            aggregate_data_grid_outage_stats = get_grid_stats(agg_dict['aggregate_data_grid_data'], 0, 'min', 10)
            aggregate_data_alerts = Sesh_Alert.objects.filter(site=site, date=date_to_fetch)
            agg_dict['sum_power_pv'] = agg_dict['aggregate_data_AC'] - agg_dict['aggregate_data_grid']
            """

            #print agg_dict
            # Create model of aggregates
            daily_aggr = Daily_Data_Point(
                                         site = site,
                                         daily_pv_yield = agg_dict['aggregate_data_pv'],
                                         daily_power_consumption_total = agg_dict['aggregate_data_AC'],
                                         daily_battery_charge = agg_dict['aggregate_data_batt'],
                                         daily_power_cons_pv = agg_dict['sum_power_pv'],
                                         daily_grid_usage = agg_dict['aggregate_data_grid'],
                                         daily_grid_outage_t = aggregate_data_grid_outage_stats['duration'],
                                         daily_grid_outage_n = aggregate_data_grid_outage_stats['count'],
                                         daily_no_of_alerts = aggregate_data_alerts.count(),
                                         date = date_to_fetch,
                                            )
            #print "saving daily aggreagete for %s dp:%s"%(date_to_fetch,daily_aggr)
            try:
                daily_aggr.save()
            except IntegrityError,e:
                logger.debug('aggregate data point not unique skipping')
                pass
            except Exception,e:
                logger.exception('Unkown error occured aggregatin data')
                message = "error with creating data point  data exception %s"%(e)
                logger.debug(message)
                logger.exception( message )
                handle_task_failure(message = message, name= 'get_aggregate_daily_data')

                pass
            #send to influx
            send_to_influx(daily_aggr, site, date_to_fetch, to_exclude=['date'], send_status=False)



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

@shared_task
def send_reports(duration="week"):
    """
    Schedule email report sending
    options: month, week, day
    """

    sites = Sesh_Site.objects.all()
    for site in sites:
        logger.debug("Sending report for site %s"%site)
        result = prepare_report(site, duration=duration)
        if not result:
            send_reports.update_state(
                             state = states.FAILURE,
                             meta = 'Something went wrong creating report  check logs'
                             )
@shared_task
def rmc_status_update():
    """
    Calculate BoM_Data_Point related RMC Status. RMC based status are calculated by kraken
    """
    logger.debug("Getting rmc status")
    sites = Sesh_Site.objects.all()
    for site in sites:
        # TODO get latest DP from influx
        latest_dp = get_latest_point_site(site,'status')
        logger.debug("getting status from site %s with dp %s"%(site,latest_dp))
        if latest_dp:
            #localize to time of site
            dp_time = time_utils.convert_influx_time_string(latest_dp['time'],tz=site.time_zone)
            last_contact = time_utils.get_timesince_seconds(dp_time, tz=site.time_zone)
            tn = timezone.localtime(timezone.now())
            last_contact_min = last_contact / 60

            # Get RMC account
            rmc_status = RMC_status(site = site,
                                    minutes_last_contact = last_contact_min,
                                    time = tn)
            logger.debug("rmc status logger now: %s last_contact: %s "%(tn,dp_time))
            logger.debug("saving status %s "%rmc_status)
            rmc_status.save()
        else:
            logger.warning("RMC STATUS: No DP found for site")


@shared_task
def alert_engine():
    """
    Periodic task to check rules agains data points
    """
    alert_generator()
    alert_status_check()

def download_vrm_historical_data():
    """
    Helper function to initiate one time download
    """
    for site in Sesh_Site.objects.filter(vrm_site_is__isnull=True):
        if site.vrm_site_id:
            get_historical_BoM.delay(site.pk,time_utils.get_epoch_from_datetime(site.comission_date))
            run_aggregate_on_historical(site.pk)
