# Test
from django.test import TestCase, Client

# Models
from seshdash.models import Sesh_Site,VRM_Account,Sesh_User
from django.contrib.auth.models import User

# Django
from guardian.shortcuts import assign_perm
from geoposition import Geoposition

# Utils
from datetime import datetime

from django.utils import timezone

class dynamic_graph_TestCase(TestCase):

    #@override_settings(DEBUG=True)
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


        #create test user
        self.test_user = User.objects.create_user("patrick", "alp@gle.solar", "cdakcjocajica")
        self.test_sesh_user = Sesh_User.objects.create(user=self.test_user,phone_number='250786688713' )
        #assign a user to the sites


        assign_perm("view_Sesh_Site",self.test_user,self.site)


    # This test case written to test post request if it returns code 200
    #Testing Time_Series_graph
    def test_time_graph(self):
        c = Client()
        c.login(username = "patrick",password = "cdakcjocajica")
        measurement_value ='pv_production'
        time_value = '24h'
        active_site_id = 1
        response = c.post('/time_series/',{'measurement':measurement_value,'time':time_value,'active_id':active_site_id})
        self.assertEqual(response.status_code , 200)

