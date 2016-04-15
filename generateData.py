from django.utils import timezone
from seshdash.models import Daily_Data_Point, BoM_Data_Point
from seshdash.utils.time_utils import get_time_interval_array
from seshdash.test.data_aggregation import get_random_int, get_random_binary, get_random_interval, generate_date_array


def create_test_data():
        print "Creating  data points "
        data_point_dates = generate_date_array(weeks=40)
        print data_point_dates
        voltage_in = 220
        voltage_out = 220
        # Simulate Grid outage
        for time_val in data_point_dates:
                dp = BoM_Data_Point.objects.create(
                                            site=self.site,
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
                self.i.send_object_measurements(dp_dict,timestamp=time_val.isoformat(),tags={"site_name":self.site.site_name})
        return len(data_point_dates)

def generate_test_data():
    create_test_data()
