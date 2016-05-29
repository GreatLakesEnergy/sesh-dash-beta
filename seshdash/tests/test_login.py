from django.test import TestCase, Client

# Testing models
from seshdash.models import Sesh_Alert, Alert_Rule, Sesh_Site,VRM_Account, BoM_Data_Point as Data_Point, Sesh_RMC_Account

# Testing forms
from seshdash.forms import SiteForm, VRMForm, RMCForm, SiteRMCForm
from django.forms import inlineformset_factory, modelformset_factory

# Utils
from django.utils import timezone
from django.contrib.auth.models import User
from seshdash.utils import rmc_tools
from datetime import datetime

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


        self.data = {
                 'form-0-site_name':u"Test site",
                 'form-0-comission_date':timezone.datetime(2015, 12, 11, 22, 0),
                 'form-0-location_city':u"kigali",
                 'form-0-location_country':u"rwanda",
                 'form-0-installed_kw':123.0,
                 'form-0-position_0':36,
                 'form-0-position_1':42,
                 'form-0-system_voltage':12,
                 'form-0-number_of_panels':12,
                 'form-0-battery_bank_capacity':12321,
                 'form-0-has_genset':True,
                 'form-0-has_grid':True,
                 'form-TOTAL_FORMS': '1',
                 'form-INITIAL_FORMS': '0',
                 'form-MIN_NUM_FORMS': '',
                 'form-MAX_NUM_FORMS': '',
                }

    def test_user_site_creation(self):
        """
        See if victron sight importing works
        """
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


    def test_vrm_site_form(self):
        """
        Test Creation of RMC form
        """

        self.data = {
                 'form-0-site_name':u"Test site",
                 'form-0-comission_date': datetime(2015, 12, 11, 22, 0),
                 'form-0-location_city':u"kigali",
                 'form-0-location_country':u"rwanda",
                 'form-0-installed_kw':123.0,
                 'form-0-position_0':36,
                 'form-0-position_1':42,
                 'form-0-system_voltage':12,
                 'form-0-number_of_panels':12,
                 'form-0-battery_bank_capacity':12321,
                 'form-0-has_genset':True,
                 'form-0-has_grid':True,
                 'form-TOTAL_FORMS': '1',
                 'form-INITIAL_FORMS': '0',
                 'form-MIN_NUM_FORMS': '',
                 'form-MAX_NUM_FORMS': '',
                }

        form_factory = modelformset_factory(
                                    Sesh_Site,
                                    form = SiteForm,
                                    can_delete = False,
                                    exclude = ('Delete','vrm_account','vrm_site_id','rmc_account','time_zone'),
                                    extra = 1
                                    )

        form = form_factory(self.data)
        form_status = form.is_valid()
        self.assertTrue(form_status)

        form.save()

        sites = Sesh_Site.objects.all()
        self.assertEqual(len(sites),1)

        site = sites[0]
        self.assertEqual(site.time_zone,'Asia/Baghdad')



    def test_rmc_site_form(self):
        """
        Test Creation of RMC form
        """

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
                 'form-TOTAL_FORMS':1,
                 'form-INITIAL_FORMS':0,
                 'form-MAX_NUM_FORMS':1,
                 'form-MIN_NUM_FORMS':1,
                }

        form_factory = modelformset_factory(
                                    Sesh_Site,
                                    form=SiteRMCForm,
                                    can_delete=False,
                                    extra=1)


        form = form_factory(self.data)
        self.assertTrue(form.is_valid())
        form.save()

        site = Sesh_Site.objects.all()







