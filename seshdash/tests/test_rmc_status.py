# Testing
from django.test import TestCase

# APP Models
from seshdash.models import Sesh_Alert, Alert_Rule, Sesh_Site,VRM_Account, BoM_Data_Point as Data_Point, Daily_Data_Point, RMC_status, Sesh_RMC_Account

# django Time related
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import timedelta
from time import sleep
import pytz


#Security
from guardian.shortcuts import assign_perm
from geoposition import Geoposition


# To Test
from seshdash.data.db.influx import Influx, insert_point, get_measurements_latest_point
from django.conf import settings
from seshdash.tasks import get_aggregate_daily_data, rmc_status_update


# This test case written to test alerting module.
# It aims to test if the system sends an email and creates an Sesh_Alert object when an alert is triggered.
class RMCTestCase(TestCase):
    def setUp(self):

        self.VRM = VRM_Account.objects.create(vrm_user_id='asd@asd.com',vrm_password="asd")
        self.location = Geoposition(52.5,24.3)
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
        self.test_rmc_account = Sesh_RMC_Account.objects.create(site = self.site, api_key='lcda5c15ae5cdsac464zx8f49asc16a')

        timestamp = timezone.localtime(timezone.now()) - timedelta(minutes=60)
        #print ""
        #print timestamp
        #timestamp = timezone.now()
        self.i.insert_point(self.site,'status', 1, time = timestamp)

        sleep(1)
        self.test_user = User.objects.create_user("john doe","alp@gle.solar","asdasd12345")
        #assign a user to the sites
        assign_perm("view_Sesh_Site",self.test_user,self.site)


    def tearDown(self):
        #self.i.delete_database(self._influx_db_name)
        pass

    def test_rmc_stat(self):
        """
        Check that when a bom data point is added that the corresponding rmc status is triggered
        """
        rmc_status_update()

        dps = RMC_status.objects.filter(site=self.site)
        self.assertNotEqual(dps.count(), 0)

        sleep(2)
        dps = dps.first()
        self.assertEqual(dps.minutes_last_contact, 60)


