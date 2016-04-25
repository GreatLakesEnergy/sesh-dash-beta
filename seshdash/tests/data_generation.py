from random import random
from random import uniform
from datetime import datetime
from django.utils import timezone
from datetime import timedelta
from django.forms import model_to_dict


from seshdash.data.db.influx import Influx
from seshdash.models import BoM_Data_Point as Data_Point
from seshdash.utils.time_utils import get_time_interval_array

# models
from seshdash.models import Sesh_Site, Daily_Data_Point

def get_random_int():
    val =  random() * 100
    return int(val)

def get_random_float():
    val = random() * 100
    return val

def get_random_binary():
    val = get_random_int()
    if val > 50:
        return 1
    return 0

def get_random_interval(cieling,floor):
    return uniform(cieling,floor)

def generate_date_array(start=None,naive=False,interval=5, units='minutes'):
    now = timezone.now()
    if naive:
        now = datetime.now()
    
    if not start:
        start = now - timedelta(hours=24)

    time_arr = get_time_interval_array(interval, units,start,now)
    return time_arr




def create_test_data(site):
        #TODO test weekly and monthly reports

        _influx_db_name = 'test_db'
        i = Influx(database=_influx_db_name)
        data_point_dates = generate_date_array()
        voltage_in = 220
        voltage_out = 220
        # Simulate Grid outage
        for time_val in data_point_dates:
                dp = Data_Point.objects.create(
                                            site=site,
                                            soc=get_random_int(),
                                            battery_voltage=get_random_interval(22,28),
                                            time=time_val,
                                            AC_Voltage_in=voltage_in * get_random_binary(),
                                            AC_Voltage_out=voltage_out,
                                            AC_input=get_random_interval(100,500),
                                            AC_output=get_random_interval(-500,500),
                                            AC_output_absolute=get_random_interval(100,500),
                                            AC_Load_in=get_random_interval(100,500),
                                            AC_Load_out=get_random_interval(100,500),
                                            pv_production=get_random_interval(100,500))
                # Also send ton influx
                dp_dict = model_to_dict(dp)
                dp_dict.pop('time')
                dp_dict.pop('inverter_state')
                dp_dict.pop('id')
                i.send_object_measurements(dp_dict,timestamp=time_val.isoformat(),tags={"site_name":site.site_name})
        return len(data_point_dates)
 



def create_test_data_daily_points (site_id, number_days=355):
    """ Generates test data for daily data points for a given site for a given number of days """

    start_date = timezone.now() - timedelta(days=number_days)
    data_point_dates = generate_date_array(start=start_date, interval=24, units='hours')
    total_items = len(data_point_dates)
    count = 0
    done = 0
    increment = 100
    site = Sesh_Site.objects.filter(pk=site_id).first()
    # Simulate Grid outage
    for time_val in data_point_dates:
              dp = Daily_Data_Point.objects.create(
                                            site=site,
                                            daily_battery_charge=get_random_float(),
                                            daily_grid_outage_n=get_random_float(),
                                            daily_grid_outage_t=get_random_float(),
                                            daily_grid_usage=get_random_float(),
                                            daily_no_of_alerts=get_random_float(),
                                            daily_power_cons_pv=get_random_float(),
                                            daily_power_consumption_total=get_random_float(),
                                            daily_pv_yield=get_random_float(),
                                            date=time_val
                                            )

              dp.save()
              count = count + 1
              done = done + 1
 
              if count % increment == 0:
                  print "100 items Done, %s to go" % (total_items - done )
    return len(data_point_dates)


def generate_test_data_daily_points():
    """ Generates Daily Data Point for all sites """
    sites = Sesh_Site.objects.all()

    for site in sites:
        create_test_data_daily_points(site.id)

                                           
