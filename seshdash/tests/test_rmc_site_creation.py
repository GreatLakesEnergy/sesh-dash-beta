"""
Testing the process of creating 
an rmc account 
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone


from seshdash.models import Sesh_Site

class TestAddRMCSite(TestCase):
    """
    """
    def setUp(self):
        """
        Initializing the db
        """
        self.user = User.objects.create_superuser(username='test', email="test@gle.solar", password='test12345')
        self.client = Client()


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

        self.assertEqual(Sesh_Site.objects.all().count(), 1)
