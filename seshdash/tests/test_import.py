# Testing
from django.test import TestCase
from django.test.utils import override_settings

# APP Models
from seshdash.models import Sesh_User, Sesh_Alert, Alert_Rule, Sesh_Site,VRM_Account, BoM_Data_Point as Data_Point, Daily_Data_Point as ddp

# django Time related
from seshdash.utils import time_utils
from django.utils import timezone
from time import sleep
import pytz
from datetime import datetime,timedelta

#Helper Functions
from django.forms.models import model_to_dict
from django.db import transaction

#Security
from guardian.shortcuts import assign_perm
from geoposition import Geoposition

# Debug
from django.forms.models import model_to_dict

# To Test
from seshdash.data.db.influx import Influx
from seshdash.api.victron import VictronAPI
from django.conf import settings
from seshdash.tasks import get_historical_BoM, get_aggregate_daily_data,run_aggregate_on_historical, get_BOM_data


# This test case written to test alerting module.
# It aims to test if the system sends an email and creates an Sesh_Alert object when an alert is triggered.
class VRM_Import_TestCase(TestCase):
    @override_settings(DEBUG=True)
    def setUp(self):

        self.VRM = VRM_Account.objects.create(vrm_user_id='demo@victronenergy.com',vrm_password="vrmdemo")
        # Setup Influx
        self._influx_db_name = 'test_db'
        self.i = Influx(database=self._influx_db_name)
        self.no_points = 288
        try:
            self.i.create_database(self._influx_db_name)
            #Generate random data  points for 24h
        except Exception, e:
           print e
           self.i.delete_database(self._influx_db_name)
           sleep(1)
           self.i.create_database(self._influx_db_name)
           pass

        self.VRM_API = VictronAPI(self.VRM.vrm_user_id, self.VRM.vrm_password)

        if self.VRM_API.IS_INITIALIZED:
           sites = self.VRM_API.SYSTEMS_IDS
           print sites
           if len(sites) > 1:
               self.vrm_site_id = sites[0][0]

        self.location = Geoposition(52.5,24.3)
        self.now = timezone.now()
        self.start_date = self.now - timedelta(days=2)

        self.site = Sesh_Site.objects.create(site_name=u"Test_aggregate",
                                             comission_date=self.start_date,
                                             location_city=u"kigali",
                                             location_country=u"rwanda",
                                             vrm_account = self.VRM,
                                             installed_kw=123.0,
                                             position=self.location,
                                             system_voltage=12,
                                             number_of_panels=12,
                                             vrm_site_id=self.vrm_site_id,
                                             battery_bank_capacity=12321,
                                             has_genset=True,
                                             has_grid=True,
                                             has_pv=True)


        #create test user
        self.test_user = Sesh_User.objects.create_user(username="john doe",email="alp@gle.solar",password="asdasd12345")
        #assign a user to the sites
        assign_perm("view_Sesh_Site",self.test_user,self.site)


    def tearDown(self):
        self.i.delete_database(self._influx_db_name)
        pass

    def test_api_stats(self):
        """
        Test Victron API points
        """
        stats = self.VRM_API.get_system_stats(self.vrm_site_id)
        self.assertTrue(stats.has_key('Input power 1'))
        stats = self.VRM_API.get_battery_stats(self.vrm_site_id)
        self.assertTrue(stats.has_key('Battery voltage'))
        #stats = self.VRM_API.get_pv_stats(self.vrm_site_id)
        #self.assertTrue(stats.has_key('PV - DC-coupled'))

        #print self.VRM_API.ATTRIBUTE_DICT

    def test_bom_data_point(self):
        get_BOM_data()
        sleep(1)
        bom_data = Data_Point.objects.all()
        #Commenting out the test
        #TODO: UNCOMMENT THIS AND FIX THE PROBLEMS WITH GETTING DATA FROM VICTON
        self.assertEqual(len(bom_data),1)


