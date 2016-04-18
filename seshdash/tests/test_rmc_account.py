# Test
from django.test import TestCase, Client
from django.test.utils import override_settings

# Models
from seshdash.models import Sesh_Alert, Alert_Rule, Sesh_Site,VRM_Account, BoM_Data_Point as Data_Point, Sesh_RMC_Account, RMC_status, Sesh_User
from django.contrib.auth.models import User

# Tasks
from seshdash.tasks import generate_auto_rules, rmc_status_update

# Django
from guardian.shortcuts import assign_perm
from geoposition import Geoposition
from django.conf import settings

# Utils
from datetime import datetimea,timedelta
from seshdash.utils import alert
from django.utils import timezone

class RMCTestCase(TestCase):

    @override_settings(DEBUG=True)
    def setUp(self):

        self.location = Geoposition(52.5,24.3)

        self.site = Sesh_Site.objects.create(site_name=u"Test site",
                                             comission_date=timezone.datetime(2015, 12, 11, 22, 0),
                                             location_city=u"kigali",
                                             location_country=u"rwanda",
                                             installed_kw=123.0,
                                             position=self.location,
                                             system_voltage=24,
                                             number_of_panels=12,
                                             vrm_site_id=213,
                                             battery_bank_capacity=12321,
                                             has_genset=True,
                                             has_grid=True)

        #create sesh rmc account
        self.test_rmc_account = Sesh_RMC_Account.objects.create(api_key='lcda5c15ae5cdsac464zx8f49asc16a')

        self.data_point = Data_Point.objects.create(site=self.site,
                                                    soc=10,
                                                    battery_voltage=20,
                                                    time=timezone.now()-timdelta(minutes=10),
                                                    AC_input=0.0,
                                                    AC_output=15.0,
                                                    AC_Load_in=0.0,
                                                    AC_Load_out=-0.7)

    def test_status_generation(self):
        """ test api key generation  working correctly"""
        rmc_status_update()
        rmc_stats = RMC_status.objects.all()
        # Check taht an RMC status was created
        self.assertEqual(len(RMC_status), 1)
        # Check that is has a None NULL value for minutes_last_contact
        rmc_stat = rmc_stats.pop()
        self.assertEqual(rmc_stat.minutes_last_contact, 10)




