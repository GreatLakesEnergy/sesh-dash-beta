# Testing
from django.test import TestCase, Client
from django.test.utils import override_settings

# APP Models
from seshdash.models import Sesh_User, Sesh_Alert, Alert_Rule, Sesh_Site,VRM_Account, BoM_Data_Point as Data_Point, Daily_Data_Point

# django Time related
from django.utils import timezone
from django.contrib.auth.models import User
from time import sleep
import pytz
from datetime import timedelta

#Helper Functions
from django.forms.models import model_to_dict
from django.core import mail

#Security
from guardian.shortcuts import assign_perm
from geoposition import Geoposition

#Data generations
from data_generation import get_random_int, get_random_binary, get_random_interval, generate_date_array, get_random_float, create_test_data

# Debug
from django.forms.models import model_to_dict

# To Test
from seshdash.utils.time_utils import get_time_interval_array
from seshdash.data.db.influx import Influx
from django.conf import settings
from seshdash.tasks import get_aggregate_daily_data, get_aggregate_data, get_grid_stats, find_chunks
from seshdash.utils.reporting import send_report


# This test case written to test alerting module.
# It aims to test if the system sends an email and creates an Sesh_Alert object when an alert is triggered.
class AggregateTestCase(TestCase):
    def setUp(self):

        self.VRM = VRM_Account.objects.create(vrm_user_id='asd@asd.com',vrm_password="asd")
        # Setup Influx
        self.i = Influx()
        self.i.create_database('test_db')
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
                                             has_grid=True,
                                             has_pv=True,
                                             has_batteries=True)

        self.test_user = Sesh_User.objects.create_user("john doe","alp@gle.solar","asdasd12345")
        #assign a user to the sites
        try:
            self.i.create_database(self._influx_db_name)
            #Generate random data  points for 24h
            self.no_points = create_test_data(self.site)
        except Exception,e:
           self.i.delete_database(self._influx_db_name)
           sleep(1)
           self.i.create_database(self._influx_db_name)
           print e
           pass

        assign_perm("view_Sesh_Site",self.test_user,self.site)

    def tearDown(self):
        self.i.delete_database(self._influx_db_name)
        pass

    def test_chunks(self):
        data =  [{u'min': 220, u'time': u'2017-02-22T10:20:00Z'}, {u'min': 220, u'time': u'2017-02-22T10:30:00Z'}, {u'min': 0, u'time': u'2017-02-22T10:40:00Z'}, {u'min': 0, u'time': u'2017-02-22T10:50:00Z'}, {u'min': 0, u'time': u'2017-02-22T11:00:00Z'}, {u'min': 0, u'time': u'2017-02-22T11:10:00Z'}, {u'min': 220, u'time': u'2017-02-22T11:20:00Z'}, {u'min': 220, u'time': u'2017-02-22T11:30:00Z'}, {u'min': 220, u'time': u'2017-02-22T11:40:00Z'}, {u'min': 0, u'time':u'2017-02-22T11:50:00Z'}, {u'min': 220, u'time':u'2017-02-22T11:50:00Z'}]

        chunked = find_chunks(data,'min')
        self.assertEqual(sum(map(lambda x: x.values().pop(),chunked)),len(data)) # Test if the value add up to total elements

    def test_grid_stats(self):
        data =  [{u'min': 220, u'time': u'2017-02-22T10:20:00Z'}, {u'min': 220, u'time': u'2017-02-22T10:30:00Z'}, {u'min': 0, u'time': u'2017-02-22T10:40:00Z'}, {u'min': 0, u'time': u'2017-02-22T10:50:00Z'}, {u'min': 0, u'time': u'2017-02-22T11:00:00Z'}, {u'min': 0, u'time': u'2017-02-22T11:10:00Z'}, {u'min': 220, u'time': u'2017-02-22T11:20:00Z'}, {u'min': 220, u'time': u'2017-02-22T11:30:00Z'}, {u'min': 220, u'time': u'2017-02-22T11:40:00Z'}, {u'min': 0, u'time':u'2017-02-22T11:50:00Z'}, {u'min': 220, u'time':u'2017-02-22T11:50:00Z'}]

        result = get_grid_stats(data, 0, 'min', 10)
        self.assertEqual(result['count'], 2)
        self.assertEqual(result['duration'], 50)


    def test_grid_outage(self):


        date_to_fetch = timezone.now() - timedelta(hours=24)
        aggregate_data_grid_data = get_aggregate_data (self.site, 'AC_Voltage_in',bucket_size='10m', toSum=False, start=date_to_fetch)

        #logging.debug("aggregate date for grid %s "%aggregate_data_grid_data)
        aggregate_data_grid_outage_stats = get_grid_stats(aggregate_data_grid_data, 0, 'min', 10)

        print aggregate_data_grid_data

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


    def test_historical_data_display(self):
        c = Client()
        c.login(username='john doe', password='asdasd12345')
        data_dict = Daily_Data_Point.UNITS_DICTIONARY
        data_keys = data_dict.keys()

        for key in data_keys:
            response = c.post('/historical_data', {"sort_value": key})
            self.assertEqual(response.status_code, 200)


