"""
Testing the process of creating
an rmc account and adding the sensors to a site
"""

# Django libs
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone

# Other libs
from geoposition import Geoposition

from seshdash.models import Sesh_Site, Sesh_RMC_Account, Sensor_EmonTh, Sensor_EmonTx, Sensor_BMV, Sensor_Mapping
from seshdash.utils.model_tools import get_all_associated_sensors, get_config_sensors

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


        self.emonth = Sensor_EmonTh.objects.create(site=self.site, node_id=5)

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


    def test_add_rmc_account(self):
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
                           'emontx-MAX_NUM_FORMS': '1000',
                           'emontx-TOTAL_FORMS': '2',
                           'emontx-INITIAL_FORMS': '0',
                           'emontx-0-node_id': '21',
                           'emontx-0-index1': 'ac_power1',
                           'emontx-0-index2': 'pv_production',
                           'emontx-0-index3': 'consumption',
                           'emontx-0-index4': 'grid_in',
                           'emontx-0-index5': 'AC_Voltage_out',
                           'emontx-0-index6': '',
                           'emontx-0-index7': '',
                           'emontx-0-index8': '',
                           'emontx-0-index9': '',
                           'emontx-0-index10': '',
                           'emontx-0-index11': '',
                           'emontx-0-index12': '',
                           'emontx-1-node_id': '22',
                           'emontx-1-index1': 'ac_power_1',
                           'emontx-1-index2': 'pv_production',
                           'emontx-1-index3': 'consumption',
                           'emontx-1-index4': 'grid_in',
                           'emontx-1-index5': 'AC_Voltage_out',
                           'emontx-1-index6': '',
                           'emontx-1-index7': '',
                           'emontx-1-index8': '',
                           'emontx-1-index9': '',
                           'emontx-1-index10': '',
                           'emontx-1-index11': '',
                           'emontx-1-index12': '',
                           'emonth-MAX_NUM_FORMS': '1000',
                           'emonth-TOTAL_FORMS': '1',
                           'emonth-INITIAL_FORMS': '0',
                           'emonth-0-node_id': '6',
                           'emonth-0-index1': 'soc',
                           'emonth-0-index2': 'battery_voltage',
                           'emonth-0-index3': 'battery_load',
                           'emonth-0-index4': 'required',
                           'bmv-MAX_NUM_FORMS': '1000',
                           'bmv-TOTAL_FORMS': '1',
                           'bmv-INITIAL_FORMS': '0',
                           'bmv-0-node_id': '29',
                           'bmv-0-index1': 'temp_fridge',
                           'bmv-0-index2': 'temp_ambient',
                           'bmv-0-index3': 'anything',
                           'bmv-0-index4': 'something',
                           'bmv-0-index5': 'something',
                           'bmv-0-index6': 'things',
                           'bmv-0-index7': 'everything',
                   })

        # Testing the rediction to the page that is shown after a rmc account is added which is the index
        self.assertEqual(response.status_code, 302)

        # Assserting the creation of the rmc site and the linking to the site
        self.assertEqual(Sesh_RMC_Account.objects.all().count(), 1)
        self.assertEqual(Sesh_RMC_Account.objects.last().site, self.site)

        # Asserting the creation fo the emon tx sensor and it linking to site
        self.assertEqual(Sensor_EmonTx.objects.all().count(), 2)
        self.assertEqual(Sensor_EmonTx.objects.last().site, self.site)

        # Asserting the creation of the emon th sensor and it linking to the site
        self.assertEqual(Sensor_EmonTh.objects.all().count(), 2) # The added one plus one in the setUp
        self.assertEqual(Sensor_EmonTh.objects.all().last().site, self.site)

        # Asserting the creation of the bmv sensor and the linking to the site
        self.assertEqual(Sensor_BMV.objects.all().count(), 1)
        self.assertEqual(Sensor_BMV.objects.all().last().site, self.site)

        # Asserting the number of sensor mappings created
        self.assertEqual(Sensor_Mapping.objects.all().count(), 5)

    def test_get_rmc_config(self):
        """
        Testing the generation of the rmc config file for a
        given file
        """

        response = self.client.get('/get_rmc_config', {'api_key': 'testing'})

        associated_sensors = get_all_associated_sensors(self.site)
        configuration, victron_device_number = get_config_sensors(associated_sensors)

        self.assertRegexpMatches(configuration, 'emonTH_1')
        self.assertRegexpMatches(configuration, 'emonPi_')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Type'), 'text/plain')

	# Testing for invalid apikeys
        response = self.client.get('/get_rmc_config', {'api_key': 'incorrect'})
        self.assertEqual(response.status_code, 403)
  
