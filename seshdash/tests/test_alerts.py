from django.test import TestCase, Client
from seshdash.models import Sesh_Alert, Alert_Rule, Sesh_Site,VRM_Account, BoM_Data_Point as Data_Point
from seshdash.utils import alert
from django.utils import timezone
from django.contrib.auth.models import User
from guardian.shortcuts import assign_perm
from geoposition import Geoposition

# This test case written to test alerting module.
# It aims to test if the system sends an email and creates an Sesh_Alert object when an alert is triggered.
class AlertTestCase(TestCase):
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
                                             number_of_pv_strings=12,
                                             Number_of_panels=12,
                                             vrm_site_id=213,
                                             battery_bank_capacity=12321,
                                             has_genset=True,
                                             has_grid=True)

        self.data_point = Data_Point.objects.create(site=self.site, soc=35.5, battery_voltage=20,
                                    time=timezone.now(),AC_input=0.0,
                                    AC_output=15.0,AC_Load_in=0.0,
                                    AC_Load_out=-0.7)
        #create test user
        self.test_user = User.objects.create_user("john doe","alp@gle.solar","asdasd12345")
        #assign a user to the sites
        assign_perm("view_Sesh_Site",self.test_user,self.site)

        Alert_Rule.objects.create(site = self.site, check_field="soc", value=30, operator="gt")
        Alert_Rule.objects.create(site = self.site, check_field="soc", value=35.5, operator="eq")
        Alert_Rule.objects.create(site = self.site, check_field="battery_voltage", value=25, operator="lt",send_mail=False)
        alert.alert_check(self.data_point)

    def test_alert_fires(self):
        """ Alert working correctly"""
        # test if necessary alerts has triggered and if alert objects saved
        alerts_created = Sesh_Alert.objects.filter(site=self.site)
        self.assertEqual(alerts_created.count(),3)
        """ Alert mails working correctly"""
        self.assertEqual(alerts_created.filter(alertSent=True).count(),2)

    # TODO add negative test cases

    def test_get_alerts(self):
        """ Getting alerts correctly """
        alerts = Sesh_Alert.objects.all().count()
        self.assertEqual(alerts, 3)

    def test_display_alert_data(self):
        """Getting the display alert data"""
        c = Client()
        response = c.post('/get-alert-data/',{'alert_id':'1'})
        self.assertEqual(response.status_code, 200)

    def test_silence_alert(self):
        """Silencing alert """
        c = Client()
        response = c.post('/silence-alert/',{'alert_id':'1'})
        alerts = Sesh_Alert.objects.filter(isSilence=False).count()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(alerts, 2)
	
    def test_get_latest_bom_data(self):
        """ Getting latest bom data"""
        c = Client()
        response = c.post('/get-latest-bom-data/',{})
        self.assertEqual(response.status_code, 200)
        
