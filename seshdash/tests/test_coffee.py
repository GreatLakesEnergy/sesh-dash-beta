# Test
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from geoposition import Geoposition


from seshdash.models import Sesh_User, Sesh_Organisation, Sesh_Site, VRM_Account, Sesh_RMC_Account, Sensor_Node
from seshdash.utils.model_tools import get_site_sensor_fields


class CoffeeTestCase(TestCase):

    def setUp(self):
        self.VRM = VRM_Account.objects.create(vrm_user_id='asd@asd.com',vrm_password="asd")

        self.location = Geoposition(52.5,24.3)

        self.organisation = Sesh_Organisation.objects.create(name='test_organisation')
    
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
                                             has_grid=True,
                                             organisation=self.organisation)

        #create test user
        self.test_sesh_user = Sesh_User.objects.create_user(username='patrick',
                                                       email='alp@gle.solar',
                                                       password='test.test.test',
                                                       phone_number='250786688713',
                                                       organisation=self.organisation)


    def test_get_site_sensor_fields(self):
        """
        Test the functions that returns the data fields for a given site, 
        the fields are got from sensor nodes
        """ 
        sensor_one = Sensor_Node.objects.create(site=self.site, index1='coffee1', index2='coffee2')
        sensor_two = Sensor_Node.objects.create(site=self.site, index1='coffee3', index2='coffee4')

        fields = get_site_sensor_fields(self.site) 
        self.assertEqual(fields, ['coffee1', 'coffee2', 'coffee3', 'coffee4'])
