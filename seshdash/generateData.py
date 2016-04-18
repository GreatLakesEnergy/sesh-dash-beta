from django.utils import timezone
from seshdash.data.db.influx import Influx
from datetime import timedelta, datetime
from django.forms import model_to_dict
from seshdash.tasks import run_aggregate_on_historical
from seshdash.models import Daily_Data_Point, BoM_Data_Point, Sesh_Site
from seshdash.utils.time_utils import get_time_interval_array
from seshdash.tests.data_generation import get_random_int, get_random_binary, get_random_interval, generate_date_array, get_random_float


def create_test_data(site_id):
        i = Influx()
        start_date = timezone.now() - timedelta(weeks=55)
        data_point_dates = generate_date_array(start=start_date, interval=24, units='hours')
        voltage_in = 220
        voltage_out = 220
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

def generate_test_data():
    sites = Sesh_Site.objects.all()
    
    for site in sites:
        create_test_data(site.id)
    
