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

from seshdash.models import Sesh_User, Sesh_Site, Sesh_RMC_Account, Sensor_Node, Sensor_Mapping
from seshdash.utils.model_tools import get_all_associated_sensors, get_config_sensors

class TestAddRMCSite(TestCase):
    """
    Testing creation of RMC site and sensor nodes
    """
    def setUp(self):
        """
        Initializing the db
        """
        self.user = Sesh_User.objects.create_superuser(username='test', email="test@gle.solar", password='test12345')
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


        self.sensor_node = Sensor_Node.objects.create(site=self.site, node_id=5)

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
                           'time_zone': 'Africa/Kigali',
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
                           'sensor_node-MAX_NUM_FORMS': '1000',
                           'sensor_node-TOTAL_FORMS': '1',
                           'sensor_node-INITIAL_FORMS': '0',
                           'sensor_node-0-node_id': '6',
                           'sensor_node-0-index1': 'soc',
                           'sensor_node-0-index2': 'battery_voltage',
                           'sensor_node-0-index3': 'battery_load',
                           'sensor_node-0-index4': 'required',
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
                           'emonpi-index1': 'testing',
                           'emonpi-index2': 'continue-testing',
                           'emonpi-index3': 'continue-testing',
                           'emonpi-index4': 'continue-testing',
                           'emonpi-index5': 'continue-testing',
                           'emonpi-index6': 'continue-testing',
                           'emonpi-index7': 'continue-testing',
                           'emonpi-index8': 'continue-testing',
                           'emonpi-index9': 'continue-testing',
                           'emonpi-index10': 'continue-testing',
                           'emonpi-index11': 'continue-testing',
                           'emonpi-index12': 'continue-testing',
                           'emonpi-index13': 'continue-testing',

                   })


        # Testing the rediction to the page that is shown after a rmc account is added which is the index
        self.assertEqual(response.status_code, 302)


        # Assserting the creation of the rmc site and the linking to the site
        self.assertEqual(Sesh_RMC_Account.objects.all().count(), 1)
        self.assertEqual(Sesh_RMC_Account.objects.last().site, self.site)

        # Asserting the creation of the emon th sensor and it linking to the site
        self.assertEqual(Sensor_Node.objects.all().count(), 2) # The added one plus one in the setUp
        self.assertEqual(Sensor_Node.objects.all().last().site, self.site)

        # Asserting the number of sensor mappings created
        self.assertEqual(Sensor_Mapping.objects.all().count(), 2)


    def test_get_rmc_config(self):
        """
        Testing the generation of the rmc config file for a
        given file
        """

        response = self.client.get('/get_rmc_config', {'api_key': 'testing'})

        associated_sensors = get_all_associated_sensors(self.site)
        configuration, victron_device_number = get_config_sensors(associated_sensors)

        self.assertRegexpMatches(configuration, 'sensor_node_1')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Type'), 'text/plain')

	# Testing for invalid apikeys
        response = self.client.get('/get_rmc_config', {'api_key': 'incorrect'})
        self.assertEqual(response.status_code, 403)

