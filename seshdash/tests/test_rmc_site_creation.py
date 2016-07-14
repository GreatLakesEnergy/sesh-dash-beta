"""
Testing the process of creating 
an rmc account 
"""

# Django libs
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone

# Other libs
from geoposition import Geoposition

from seshdash.models import Sesh_Site, Sesh_RMC_Account, Sensor_EmonTh, Sensor_EmonTx, Sensor_BMV

class TestAddRMCSite(TestCase):
    """
    """
    def setUp(self):
        """
        Initializing the db
        """
        self.user = User.objects.create_superuser(username='test', email="test@gle.solar", password='test12345')
        self.client = Client()

        self.site = Sesh_Site.objects.create(
                        site_name='test',
                        comission_date=timezone.now(),
                        location_city='Kigali',
                        location_country='Rwanda',
                        position=Geoposition(12,1),
                        installed_kw=25,
                        system_voltage=45,
                        number_of_panels=45,
                        battery_bank_capacity=450,
                    )

        self.rmc_account = Sesh_RMC_Account.objects.create(
                               site=self.site,
                               api_key='testing',
                               api_key_numeric='123456789987654321',
                           )


    def test_add_rmc_site(self):
        """
        Test Rmc site
        """
        self.client.login(username="test", password="test12345")


        response = self.client.post('/add_rmc_site', {
                           'site_name': 'test_site',
                           'comission_date': '2016-07-12',
                           'location_city': 'kigali',
                           'location_country': 'rwanda',
                           'position_0': '34',
                           'position_1': '2',
                           'installed_kw': '350',
                           'system_voltage': '45',
                           'number_of_panels': '10',
                           'battery_bank_capacity': '400',
                   })


        self.assertEqual(Sesh_Site.objects.all().count(), 2)


    def test_rmc_account(self):
        """
        Testing the creation of the rmc account
        and the association to the site
        also test the creation of the sensors and 
        their association to the site
        """
        self.client.login(username="test", password="test12345")
    
        url = '/add_rmc_account/' + str(self.site.id)

        response = self.client.post(url, {
                           'api_key': 'testing12345',
                           'api_key_numeric': '987654321123456789',
                           'sensor': ['BMV','Emon Tx'],
                   })
    
        # Testing the rediction to the page that is shown after a rmc account is added which is the index
        self.assertEqual(response.status_code, 302)

        # Assserting the creation of the rmc site and the linking to the site
        self.assertEqual(Sesh_RMC_Account.objects.all().count(), 1)
        self.assertEqual(Sesh_RMC_Account.objects.last().site, self.site)

        # Asserting the creation fo the emon tx sensor and it linking to site
        self.assertEqual(Sensor_EmonTx.objects.all().count(), 1)
        self.assertEqual(Sensor_EmonTx.objects.last().site, self.site)

        # Asserting the creation of the BMv sensor and it linking to the site
        self.assertEqual(Sensor_BMV.objects.all().count(), 1)
        self.assertEqual(Sensor_EmonTx.objects.last().site, self.site)


    def test_get_rmc_config(self):
        """
        Testing the generation of the rmc config file for a 
        given file
        """

        response = self.client.post('/get_rmc_config', {'api_key': 'testing'})

        print "The response is : ",
        print response

        print "The status code is: ",
        print response.status_code

