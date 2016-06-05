# Test
from django.test import TestCase, Client
from django.test.utils import override_settings

# Models
from seshdash.models import Sesh_Alert, Alert_Rule, Sesh_Site,VRM_Account, BoM_Data_Point as Data_Point, Sesh_RMC_Account, RMC_status, Sesh_User
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

# This test case written to test alerting module.
# It aims to test if the system sends an email and creates an Sesh_Alert object when an alert is triggered.
class SearchTestCase(TestCase):

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
        #create sesh rmc account
        self.test_rmc_account = Sesh_RMC_Account(site=self.site, api_key='lcda5c15ae5cdsac464zx8f49asc16a')
        self.test_rmc_account.save()

        #create test user
        self.test_user = User.objects.create_user("patrick", "alp@gle.solar", "cdakcjocajica")
        self.test_sesh_user = Sesh_User.objects.create(user=self.test_user,phone_number='250786688713' )
        #assign a user to the sites


        assign_perm("view_Sesh_Site",self.test_user,self.site)

        generate_auto_rules(self.site.pk)


    # Testing search
    def test_search(self):
        f = Client()
        f.login(username = "patrick",password = "cdakcjocajica")

        response = f.post('/search',{})
        self.assertEqual(response.status_code, 200)


