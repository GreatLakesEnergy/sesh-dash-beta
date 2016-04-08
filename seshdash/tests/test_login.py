from django.test import TestCase, Client
from seshdash.models import Sesh_Alert, Alert_Rule, Sesh_Site,VRM_Account, BoM_Data_Point as Data_Point
from seshdash.utils import alert
from django.utils import timezone
from django.contrib.auth.models import User
from guardian.shortcuts import assign_perm
from geoposition import Geoposition

class LoginTestCase(TestCase):
    """
    Test case for testing login procedure, RMC and victron
    """
    def setUp(self):

        #create test user
        self.test_user = User.objects.create_user("johndoe","alp@gle.solar","asdasd12345")


    def test_user_login_victron(self):
        """ See if victron sight importing works """
        c = Client()
        # Test standar login first
        c.login(username='johndoe',password='asdasd12345')

        # Postive login test case to VRM
        post_data = {'vrm_user_id':'demo@victronenergy.com','vrm_password':'vrmdemo'}
        response = c.post('/import-site/',post_data)
        self.assertEqual(response.status_code, 200)

        # Check we have the proper form_type
        form_type = response.context['form_type']
        self.assertEqual(form_type,'vrm')
