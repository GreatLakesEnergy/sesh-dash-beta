from django.test import TestCase, Client

# Testing models
from seshdash.models import Sesh_Alert, Alert_Rule, Sesh_Site,VRM_Account, BoM_Data_Point as Data_Point, Sesh_RMC_Account

# Testing forms
from seshdash.forms import SiteForm, VRMForm, RMCForm, SiteRMCForm
from django.forms import inlineformset_factory

# Utils
from django.utils import timezone
from django.contrib.auth.models import User
from seshdash.utils import rmc_tools

# Shortcuts
from guardian.shortcuts import assign_perm

# Misc
from geoposition import Geoposition

class LoginTestCase(TestCase):
    """
    Test case for testing login procedure, RMC and victron
    """
    def setUp(self):

        #create test user
        self.test_user = User.objects.create_user("johndoe","alp@gle.solar","asdasd12345")

        self.location = Geoposition(52.5,24.3)

        self.data = {
                 'site_name':u"Test site",
                 'comission_date':timezone.datetime(2015, 12, 11, 22, 0),
                 'location_city':u"kigali",
                 'location_country':u"rwanda",
                 'installed_kw':123.0,
                 'position':self.location,
                 'system_voltage':12,
                 'number_of_panels':12,
                 'battery_bank_capacity':12321,
                 'has_genset':True,
                 'has_grid':True,
                 'sesh_site_set-TOTAL_FORMS':1,
                 'sesh_site_set-INITIAL_FORMS':0,
                 'sesh_site_set-MAX_NUM_FORMS':1,
                }

    def test_user_site_creation(self):
        """ See if victron sight importing works """
        c = Client()
        # Test standar login first
        c.login(username='johndoe',password='asdasd12345')

        # Postive login test case to VRM
        post_data = {'vrm_user_id':'demo@victronenergy.com',
                'vrm_password':'vrmdemo',
                'form_type':'vrm'}
        response = c.post('/import-site/',post_data)
        self.assertEqual(response.status_code, 200)
        form_type = response.context['form_type']
        error = response.context.__contains__('error')

        self.assertEqual(form_type,'vrm')
        self.assertEqual(error,False)

        # Submit Form
        post_data = {}
        post_data['form_type'] = 'rmc'
        response = c.post('/import-site/',post_data)
        self.assertEqual(response.status_code, 200)
        form_type = response.context['form_type']
        self.assertEqual(form_type,'rmc')



    def test_rmc_site_form(self):

        form_factory = inlineformset_factory(Sesh_RMC_Account,
                                    Sesh_Site,
                                    form=SiteRMCForm,
                                    can_delete=False,
                                    extra=1)

        rmc = Sesh_RMC_Account.objects.create(api_key=rmc_tools.generate_rmc_api_key())
        rmc.save()

        form = form_factory(self.data, instance=rmc)
        self.assertTrue(form.is_valid())
        form.save()



