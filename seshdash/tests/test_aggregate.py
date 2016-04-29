# Testing
from django.test import TestCase, Client
from django.test.utils import override_settings

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
from data_generation import get_random_int, get_random_binary, get_random_interval, generate_date_array, get_random_float

# Debug
from django.forms.models import model_to_dict

# To Test
from seshdash.utils.time_utils import get_time_interval_array
from seshdash.data.db.influx import Influx
from django.conf import settings
from seshdash.tasks import get_aggregate_daily_data, send_reports
from seshdash.tests.data_generation import create_test_data


# This test case written to test alerting module.
# It aims to test if the system sends an email and creates an Sesh_Alert object when an alert is triggered.
class AggregateTestCase(TestCase):
    def setUp(self):

        self.VRM = VRM_Account.objects.create(vrm_user_id='asd@asd.com',vrm_password="asd")
        # Setup Influx
        self._influx_db_name = 'test_db'
        self.i = Influx(database=self._influx_db_name)
        self.no_points = 288
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

        self.test_user = User.objects.create_user("john doe","alp@gle.solar","asdasd12345")
        #assign a user to the sites
        try:
            self.i.create_database(self._influx_db_name)
            #Generate random data  points for 24h
            self.no_points = create_test_data(self.site)
        except Exception,e:
           #self.i.delete_database(self._influx_db_name)
           #sleep(1)
           #self.i.create_database(self._influx_db_name)
           pass

        assign_perm("view_Sesh_Site",self.test_user,self.site)

    def tearDown(self):
        #self.i.delete_database(self._influx_db_name)
        pass


    def test_grid_outage(self):
        # TODO
        #aggregate_data_grid_data = get_aggregate_data (site, 'AC_Voltage_in',bucket_size='10m', toSum=False, start=date_to_fetch)

        #logging.debug("aggregate date for grid %s "%aggregate_data_grid_data)
        #aggregate_data_grid_outage_stats = get_grid_stats(aggregate_data_grid_data, 0, 'min', 10)

        pass

    @override_settings(INFLUX_DB='test_db')
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

    @override_settings(INFLUX_DB='test_db')
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
        self.assertNotEqual(ddp.daily_grid_usage,0)

    @override_settings(INFLUX_DB='test_db')
    def test_reporting(self):
        """
        Test email reporting for sites
        """
        settings.INFLUX_DB = self._influx_db_name
        get_aggregate_daily_data()
        send_reports("day")
        self.assertEqual(len(mail.outbox),1)


    def test_historical_data_display(self):
        c = Client()
        c.login(username='john doe', password='asdasd12345')
        data_dict = Daily_Data_Point.UNITS_DICTIONARY
        data_keys = data_dict.keys()

        for key in data_keys:
            response = c.post('/historical_data', {"sort_value": key})
            self.assertEqual(response.status_code, 200)


