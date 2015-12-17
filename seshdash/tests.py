from django.test import TestCase
from seshdash.models import Sesh_Alert, Alert_Rule, Sesh_Site, BoM_Data_Point as Data_Point
from seshdash.utils import alert
from django.utils import timezone

# This test case written to test alerting module.
# It aims to test if the system sends an email and creates an Sesh_Alert object when an alert is triggered.
class AlertTestCase(TestCase):
    def setUp(self):
        self.site = Sesh_Site.objects.create(site_name=u"Test site", comission_date=timezone.datetime(2015, 12, 11, 22, 0),
                                    location_city=u"kigali", location_country=u"rwanda", latitude=2.0, longitude=-2.0,
                                    installed_kw=123.0, number_of_pv_strings=12, Number_of_panels=12, vrm_user_id=u"asdasd",
                                    vrm_password=u"asdads", vrm_site_id=213, battery_bank_capacity=12321, has_genset=True,
                                    has_grid=True)
        self.data_point = Data_Point.objects.create(site=self.site, soc=35.5, battery_voltage=20,
                                    time=timezone.now(),AC_input=0.0,
                                    AC_output=15.0,AC_Load_in=0.0,
                                    AC_Load_out=-0.7)
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
