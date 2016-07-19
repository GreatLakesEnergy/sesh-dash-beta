from django.test import TestCase, Client
from django.test.utils import override_settings
#models
from seshdash.models import Site_Weather_Data,VRM_Account,Sesh_Site,Status_Rule,BoM_Data_Point,Site_Measurements

from geoposition import Geoposition
from django.conf import settings
#utils
from django.utils import timezone
from seshdash.utils.model_tools import get_quick_status,get_site_measurements
from django.contrib.auth.models import User
from seshdash.data.db.influx import Influx

class StatusTestCase(TestCase):
    @override_settings(DEBUG=True)
    def setUp(self):

        self.db_name = 'test_db'
        self.Client = Influx()
        try:
            self.Client.create_database(self.db_name)
        except:
            self.Client.delete_database(self.db_name)
            sleep(1)
            self.Client.create_database(self.db_name)
            pass

        self.vrm = VRM_Account.objects.create(vrm_user_id='user@user.user',vrm_password='password')
        self.location = Geoposition(-1.5,29.5)
        #create Sesh_Site
        self.site = Sesh_Site.objects.create(site_name='Mukuyu',
                                             comission_date = timezone.datetime(2014,12,12,12,12),
                                             location_city='kigali',
                                             location_country='Rwanda',
                                             vrm_account=self.vrm,
                                             installed_kw=123.0,
                                             position=self.location,
                                             system_voltage=24,
                                             number_of_panels=12,
                                             vrm_site_id=213,
                                             battery_bank_capacity=1200,
                                             has_genset = True,
                                             has_grid=True)

        #creating Site_Weather_Data
        self.site_weather = Site_Weather_Data.objects.create(site = self.site,
                                                             date = timezone.datetime(2016, 10, 10, 10, 10),
                                                             temp = 0,
                                                             condition = "none",
                                                             cloud_cover = 1,
                                                             sunrise = timezone.now(),
                                                             sunset = timezone.now())

        User.objects.create_superuser(username='frank',password='password',email='frank@frank.frank')

    def test_status(self):
        #insert_point in influx
        self.Client.insert_point(self.site,'soc',20.0)
        sites = Sesh_Site.objects.all()
        response = get_quick_status(sites)
        self.assertEqual(response[0]['battery'],'red')
        self.assertEqual(response[0]['weather'],'yellow')

    #testing get_site_measurements function
    def test_get_measurements(self):
        site_measurements = get_site_measurements(self.site)
        measurements = Site_Measurements.objects.all()
        print site_measurements
        self.assertEqual(len(measurements),1)
