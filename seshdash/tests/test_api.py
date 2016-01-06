from django.test import TestCase
from seshdash.models import Sesh_Alert, Alert_Rule, Sesh_Site,VRM_Account, BoM_Data_Point as Data_Point
from django.utils import timezone
from django.contrib.auth.models import User
from guardian.shortcuts import assign_perm


# This test case written to test API module.
class APITestCase(TestCase):
    def setUp(self):
        self.VRM = VRM_Account.objects.create(vrm_user_id='asd@asd.com',vrm_password="asd")

        self.site = Sesh_Site.objects.create(site_name=u"Test site",
                                             comission_date=timezone.datetime(2015, 12, 11, 22, 0),
                                             location_city=u"kigali",
                                             location_country=u"rwanda",
                                             latitude=2.0,
                                             longitude=-2.0,
                                             vrm_account = self.VRM,
                                             installed_kw=123.0,
                                             number_of_pv_strings=12,
                                             Number_of_panels=12,
                                             vrm_site_id=213,
                                             battery_bank_capacity=12321,
                                             has_genset=True,
                                             has_grid=True)

        self.data_point = Data_Point.objects.create(site=self.site, soc=35.5, battery_voltage=20,
                                    time=timezone.now(),AC_input=0.0,
                                    AC_output=15.0,AC_Load_in=0.0,
                                    AC_Load_out=-0.7)
        #create test user
        self.test_user = User.objects.create_user("john doe","alp@gle.solar","asdasd12345")
        #assign a user to the sites
        assign_perm("view_Sesh_Site",self.test_user,self.site)


    def test_api_connects(self):
        """ API's workng correctly """
        #TODO Use configs in settings.ini
        sites_created = VRM_Account.objects.all()
        self.assertEqual(sites_created.count(),1)

