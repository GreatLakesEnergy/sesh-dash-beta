# Test
from django.test import TestCase, Client
from django.test.utils import override_settings

# Models
from seshdash.models import Sesh_User, Sesh_Alert, Alert_Rule, Sesh_Site,VRM_Account, BoM_Data_Point as Data_Point, Sesh_RMC_Account, RMC_status
from django.contrib.auth.models import User

# Tasks
from seshdash.tasks import generate_auto_rules

# Django
from guardian.shortcuts import assign_perm
from geoposition import Geoposition
from django.conf import settings

# Utils
from datetime import datetime
from seshdash.utils import alert
from django.utils import timezone
# Influx
from influxdb import InfluxDBClient
from seshdash.data.db.influx import Influx

# This test case written to test post request if it returns code 200
class graph_TestCase(TestCase):

    @override_settings(DEBUG=True)
    def setUp(self):
        self.VRM = VRM_Account.objects.create(vrm_user_id='asd@asd.com',vrm_password="asd")

        self.location = Geoposition(52.5,24.3)

        self.site = Sesh_Site.objects.create(site_name=u"Test site",
                                             comission_date=timezone.datetime(2015, 12, 11, 22, 0),
                                             location_city=u"kigali",
                                             location_country=u"rwanda",
                                             vrm_account = self.VRM,
                                             installed_kw=123.0,
                                             position=self.location,
                                             system_voltage=24,
                                             number_of_panels=12,
                                             vrm_site_id=213,
                                             battery_bank_capacity=12321,
                                             has_genset=True,
                                             has_grid=True)

        self.data_point = Data_Point.objects.create(site=self.site,
                                                    soc=10,
                                                    battery_voltage=20,
                                                    time=timezone.now(),
                                                    AC_input=0.0,
                                                    AC_output=15.0,
                                                    AC_Load_in=0.0,
                                                    AC_Load_out=-0.7)
        #create test user
        self.test_sesh_user = Sesh_User.objects.create_user(username='patrick',
                                                       email='alp@gle.solar',
                                                       password='test.test.test',
                                                       phone_number='250786688713')
        #assign a user to the sites


        assign_perm("view_Sesh_Site", self.test_sesh_user, self.site)


    # Testing graph
    def test_graph(self):
        f = Client()
        f.login(username = "patrick",password = "test.test.test")
        choices = ['pv_production','soc']
        time = '24h'
        active_site_id = 1
        response = f.post('/graphs',{ 'choice': choices,'time':time , 'active_site_id': active_site_id })
        self.assertEqual(response.status_code, 200)


