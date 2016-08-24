
from django.test import TestCase, Client
from django.test.utils import override_settings

# Models
from seshdash.models import Sesh_Alert, Alert_Rule, Sesh_Site,VRM_Account, BoM_Data_Point as Data_Point, Sesh_RMC_Account, RMC_status, Sesh_User, Site_Weather_Data
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

        self.site = Sesh_Site.objects.create(
                        site_name='test',
                        comission_date=timezone.now(),
                        location_city='Kigali',
                        location_country='Rwanda',
                        position=self.location,
                        installed_kw=25,
                        system_voltage=45,
                        number_of_panels=45,
                        battery_bank_capacity=450,
                   )
                        


        #create sesh rmc account
        self.test_rmc_account = Sesh_RMC_Account.objects.create(site=self.site,
                                                                api_key='lcda5c15ae5cdsac464zx8f49asc16a')



        #create test user
        self.test_user = User.objects.create_user("test_user", "alp@gle.solar", "cdakcjocajica")
        self.test_sesh_user = Sesh_User.objects.create(user=self.test_user,phone_number='250786688713' )
        #assign a user to the sites



        generate_auto_rules(self.site.pk)

        User.objects.create_superuser(username='frank',password='password',email='frank@frank.frank')


    def test_edit_site(self):
        c = Client()
        c.login(username = "frank",password = "password")
        data= {'site_name':u'kibuye',
               'comission_date':datetime(2015,12,11,22,0),
               'location_city':u'kigali',
               'location_country':u'rwanda',
               'time_zone':'Africa/Kigali',
               'position_0':36,
               'position_1':42,
               'installed_kw':2,
               'system_voltage':4,
               'number_of_panels':100,
               'site_Id':2,
               'battery_bank_capacity':1200,
               'api_key': 'testing',
               'api_key_numeric': '123456'}

        response = c.post('/edit_site/' + str(self.site.id) , data)

        # Testing if the site has been edited succesfully
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Sesh_Site.objects.first().site_name, 'kibuye')


        # Checking for another unauthorized user
        c.login(username="test_user",password="cdakcjocajica")
        response = c.post('/edit_site/' + str(self.site.id), data)
        self.assertEqual(response.status_code, 403)
