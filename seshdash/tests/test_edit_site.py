
from django.test import TestCase, Client
from django.test.utils import override_settings

# Models
from seshdash.models import Sesh_Alert, Alert_Rule, Sesh_Site,VRM_Account, BoM_Data_Point as Data_Point, Sesh_RMC_Account, RMC_status, Sesh_User
from django.contrib.auth.models import User

#Forms
from seshdash.forms import SiteForm

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

class AddTestCase(TestCase):
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
        self.test_rmc_account = Sesh_RMC_Account(api_key='lcda5c15ae5cdsac464zx8f49asc16a')
        self.test_rmc_account.save()

        #create rmc status
        self.test_rmc_status = RMC_status.objects.create(rmc=self.test_rmc_account,
                                                        ip_address='127.0.0.1',
                                                        minutes_last_contact=100,
                                                        signal_strength=27,
                                                        data_sent_24h=12,
                                                        time=datetime.now())
        self.test_rmc_status.save()

        #create test user
        self.test_user = User.objects.create_user("patrick", "alp@gle.solar", "cdakcjocajica")
        self.test_sesh_user = Sesh_User.objects.create(user=self.test_user,phone_number='250786688713' )
        #assign a user to the sites


        assign_perm("view_Sesh_Site",self.test_user,self.site)

        generate_auto_rules(self.site.pk)

    def test_edit_site(self):
        f = Client()
        f.login(username = "patrick",password = "cdakcjocajica")
        data={'site_name':u'kibuye',
                              'comission_date':datetime(2015,12,11,22,0),
                              'location_city':u'kigali',
                              'location_country':u'rwanda',
                              'time_zone':'Africa/Kigali',
                              'position_0':36,
                              'position_1':42,
                              'installed_kw':2,
                              'system_voltage':4,
                              'number_of_panels':100,
                              'battery_bank_capacity':1200}
        form = SiteForm(data)
        # checking if site is valid
        self.assertTrue(form.is_valid())
        # checking created site
        sites = Sesh_Site.objects.all()
        self.assertEqual(len(sites),1)
        response = f.post('/edit_site',data)
        self.assertEqual(response.status_code,200)
