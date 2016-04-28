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

def generate_date_array(start=None, end = 'now',  naive=False, interval=5, units='minutes'):
    if end == 'now':
        end = timezone.now()
    if naive:
        end = datetime.now()
    if not start:
        start = end - timedelta(hours=24)
    time_arr = get_time_interval_array(interval, units,start, end)
    return time_arr




def create_test_data(site, start=None, end="now", interval=5, units='minutes' ,random=True, val=50, db='test_db'):
        #TODO test weekly and monthly reports

        _influx_db_name = db
        i = Influx(database=_influx_db_name)
        data_point_dates = generate_date_array(start=start, end=end, interval=interval, units=units)
        voltage_in = 220
        voltage_out = 220
        soc = val
        R1 = val
        R2 = val
        R3 = val
        print "createing %s test data points"%len(data_point_dates)
        print "between %s and %s "%(data_point_dates[0],data_point_dates[len(data_point_dates)-1:])
        # Simulate Grid outage
        for time_val in data_point_dates:
                if random:
                    soc = get_random_int()
                    R1 = voltage_in * get_random_binary()
                    R2 = get_random_interval(100,500)
                    R3 = get_random_interval(22,28)
                    R4 = get_random_interval(100,500)
                    R5 = get_random_interval(100,500)

                dp = Data_Point.objects.create(
                                            site=site,
                                            soc = soc ,
                                            battery_voltage = R3,
                                            time=time_val,
                                            AC_Voltage_in = R1,
                                            AC_Voltage_out = voltage_out,
                                            AC_input = R4,
                                            AC_output = R5,
                                            AC_output_absolute = R2,
                                            AC_Load_in = R2,
                                            AC_Load_out = R4,
                                            pv_production = R5)
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
    print "createing %s test data points"%total_items
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


