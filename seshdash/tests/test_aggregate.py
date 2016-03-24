# Testing
from django.test import TestCase

# APP Models
from seshdash.models import Sesh_Alert, Alert_Rule, Sesh_Site,VRM_Account, BoM_Data_Point as Data_Point, Daily_Data_Point

# django Time related
from django.utils import timezone
from django.contrib.auth.models import User
from time import sleep
import pytz

#Helper Functions
from django.forms.models import model_to_dict
from django.core import mail

#Security
from guardian.shortcuts import assign_perm
from geoposition import Geoposition

#Data generations
from data_generation import get_random_int, get_random_binary, get_random_interval, generate_date_array

# Debug
from django.forms.models import model_to_dict

# To Test
from seshdash.data.db.influx import Influx
from django.conf import settings
from seshdash.tasks import get_aggregate_daily_data, send_reports


# This test case written to test alerting module.
# It aims to test if the system sends an email and creates an Sesh_Alert object when an alert is triggered.
class AggregateTestCase(TestCase):
    def setUp(self):

        self.VRM = VRM_Account.objects.create(vrm_user_id='asd@asd.com',vrm_password="asd")
        # Setup Influx
        self._influx_db_name = 'test_db'
        self.i = Influx(database=self._influx_db_name)
        self.no_points = 288
        try:
            self.i.create_database(self._influx_db_name)
            # Generate random data  points for 24h
        except:
            self.i.delete_database(self._influx_db_name)
            sleep(1)
            self.i.create_database(self._influx_db_name)

        self.location = Geoposition(52.5,24.3)

        self.site = Sesh_Site.objects.create(site_name=u"Test_aggregate",
                                             comission_date=timezone.datetime(2015, 12, 11, 22, 0),
                                             location_city=u"kigali",
                                             location_country=u"rwanda",
                                             vrm_account = self.VRM,
                                             installed_kw=123.0,
                                             position=self.location,
                                             system_voltage=12,
                                             number_of_panels=12,
                                             vrm_site_id=213,
                                             battery_bank_capacity=12321,
                                             has_genset=True,
                                             has_grid=True)

        """
        self.data_point = Data_Point.objects.create(
                site=self.site,
                soc=35.5,
                battery_voltage=20,
                time=timezone.now(),
                AC_input=0.0,
                AC_output=15.0,
                AC_Load_in=0.0,
                AC_Load_out=0.7)
        """

        self.no_points = self.create_test_data()
        #create test user
        self.test_user = User.objects.create_user("john doe","alp@gle.solar","asdasd12345")
        #assign a user to the sites
        assign_perm("view_Sesh_Site",self.test_user,self.site)

    def tearDown(self):
        #self.i.delete_database(self._influx_db_name)
        pass

    def test_data_point_creation(self):
        """
        Test all the DP were created in MYSQL and INFLUX
        """
        dps = Data_Point.objects.filter(site=self.site)
        self.assertNotEqual(dps.count(), 0)
        sleep(2)
        num_point = len(self.i.query("pv_production"))
        self.assertNotEqual(num_point,0)

        #get aggregate daily data
        get_aggregate_daily_data()

    def test_data_aggregation(self):
        """
        Test data aggregation and daily_data_point creations
        """
        get_aggregate_daily_data()
        ddp = Daily_Data_Point.objects.all()

        self.assertEqual(ddp.count(),1)
        ddp = ddp.first()
        self.assertNotEqual(ddp.daily_pv_yield,0)
        self.assertNotEqual(ddp.daily_power_consumption_total,0)
        self.assertNotEqual(ddp.daily_battery_charge,0)
        self.assertNotEqual(ddp.daily_power_cons_pv,0)
        self.assertNotEqual(ddp.daily_grid_outage_n,0)
        self.assertNotEqual(ddp.daily_grid_outage_t,0)
        self.assertNotEqual(ddp.daily_grid_usage,0)

    def test_reporting(self):
        """
        Test email reporting for sites
        """
        get_aggregate_daily_data()
        send_reports()
        self.assertEqual(len(mail.outbox),1)


    def create_test_data(self):
        print "Creating  data points "
        data_point_dates = generate_date_array()
        voltage_in = 220
        voltage_out = 220
        # Simulate Grid outage
        for time_val in data_point_dates:
                dp = Data_Point.objects.create(
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



