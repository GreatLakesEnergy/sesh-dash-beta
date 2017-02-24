# Testing
from django.test import TestCase, Client
from django.test.utils import override_settings

# APP Models
from seshdash.models import Sesh_User, Sesh_Alert, Alert_Rule, Sesh_Site,VRM_Account, BoM_Data_Point as Data_Point, Daily_Data_Point

# django Time related
from django.utils import timezone
from django.contrib.auth.models import User
from time import sleep
from datetime import timedelta
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
from seshdash.tasks import get_aggregate_daily_data
from seshdash.tests.data_generation import create_test_data


# This test case written to test alerting module.
# It aims to test if the system sends an email and creates an Sesh_Alert object when an alert is triggered.
class InfluxTestCase(TestCase):

    def setUp(self):

        self.VRM = VRM_Account.objects.create(vrm_user_id='asd@asd.com',vrm_password="asd")
        # Setup Influx
        self._influx_db_name = 'test_db'
        self.i = Influx(database=self._influx_db_name)

        try:
            self.i.create_database(self._influx_db_name)
            #Generate random data  points for 24h
        except:
           self.i.delete_database(self._influx_db_name)
           sleep(1)
           self.i.create_database(self._influx_db_name)
           pass

        self.location = Geoposition(52.5,24.3)
        dt = timezone.make_aware(timezone.datetime(2015, 12, 11, 22, 0))

        self.site = Sesh_Site.objects.create(site_name=u"Test_aggregate",
                                             comission_date = dt,
                                             location_city = u"kigali",
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

        self.no_points = create_test_data(self.site,
                                        start = self.site.comission_date,
                                        end = dt + timedelta( hours = 48),
                                        interval = 30
                                        )
        #create test user
        self.test_user = Sesh_User.objects.create_user(username="john doe",email="alp@gle.solar",password="asdasd12345")
        #assign a user to the sites
        assign_perm("view_Sesh_Site",self.test_user,self.site)

    def tearDown(self):
        self.i.delete_database(self._influx_db_name)
        pass

    @override_settings(INFLUX_DB='test_db')
    def test_influx_aggr_query(self):
        """
        Test all the DP were created in MYSQL and INFLUX
        """

        mean = self.i.get_measurement_bucket('pv_production',
                                            '1h',
                                            'site_name',
                                            self.site.site_name,
                                            operator='mean',
                                            start=self.site.comission_date)

        self.assertEqual(25,len(mean))
        self.assertEqual(50,mean[0]['mean'])



