# Test
from django.test import TestCase, Client
from django.test.utils import override_settings

# Model's
from seshdash.models import Sesh_User, Sesh_Alert, Alert_Rule, Sesh_Site,VRM_Account, BoM_Data_Point as Data_Point, Sesh_RMC_Account, RMC_status, Sesh_Organisation, Slack_Channel
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth import authenticate

# Tasks
from seshdash.tasks import generate_auto_rules

# Django
from guardian.shortcuts import assign_perm, get_groups_with_perms
from geoposition import Geoposition
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

# Influx
from seshdash.data.db.influx import Influx, insert_point

# Utils
from datetime import datetime
from seshdash.utils import alert
from django.utils import timezone
from time import sleep

# This test case written to test alerting module.
# It aims to test if the system sends an email and creates an Sesh_Alert object when an alert is triggered.
class AlertTestCase(TestCase):

    @override_settings(DEBUG=True)
    def setUp(self):

        self._influx_db_name = 'test_db'
        self.i = Influx(database=self._influx_db_name)

        try:
            self.i.create_database(self._influx_db_name)
            #Generate random data  points for 24h
        except:
           self.i.delete_database(self._influx_db_name)
           sleep(1)
           self.i.create_database(self._influx_db_name)
           pass



        self.VRM = VRM_Account.objects.create(vrm_user_id='asd@asd.com',vrm_password="asd")

        self.location = Geoposition(52.5,24.3)

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
                                             has_grid=True)


        # Creating permissions for group
        content_type = ContentType.objects.get_for_model(Sesh_Site)
        self.permission = Permission.objects.create(codename='can_manage_sesh_site',
                                                    name='Can add Sesh Site',
                                                    content_type=content_type)

        self.data_point = Data_Point.objects.create(site=self.site,
                                                    soc=10,
                                                    battery_voltage=20,
                                                    time=timezone.now(),
                                                    AC_input=0.0,
                                                    AC_output=15.0,
                                                    AC_Load_in=0.0,
                                                    AC_Load_out=-0.7)
        #create sesh rmc account
        self.test_rmc_account = Sesh_RMC_Account(site=self.site, api_key='lcda5c15ae5cdsac464zx8f49asc16a')
        self.test_rmc_account.save()

        #create rmc status
        self.test_rmc_status = RMC_status.objects.create(site=self.site,
                                                        ip_address='127.0.0.1',
                                                        minutes_last_contact=100,
                                                        signal_strength=27,
                                                        data_sent_24h=12,
                                                        time=datetime.now())
        self.test_rmc_status.save()


        #create influx datapoint
        self.influx_data_point = insert_point(self.site, 'battery_voltage', 10)

        #create test user
        self.test_user = Sesh_User.objects.create_user(username="patrick",
                                                  email="alp@gle.solar",
                                                  password="test.test.test",
                                                  phone_number='250786688713',
                                                  on_call=True,
                                                  send_mail=True,
                                                  send_sms=True)



        # Creating test group


        self.test_organisation = Sesh_Organisation.objects.create(name='test_organisation',
                                                                  send_slack=True,
                                                                  slack_token=settings.SLACK_TEST_KEY)

        # Creating test channels
        self.test_channels = Slack_Channel.objects.create(organisation=self.test_organisation,
                                                          name='test_alerts_channel',
                                                          is_alert_channel=True)

        #assign a user to the sites


        assign_perm("view_Sesh_Site",self.test_user,self.site)

        generate_auto_rules(self.site.pk)

        influx_rule = Alert_Rule.objects.create(check_field='battery_voltage',
                                                operator='lt',
                                                site=self.site,
                                                value=20)

        alert.alert_generator()


        self.new_influx_data_point = insert_point(self.site, 'battery_voltage',  24)
        sleep(2) # Added sleep to wait for sometime until the point is written to the db

        # Create data point that will silence alert
        self.new_data_point = Data_Point.objects.create(site=self.site,
                                                    soc=50,
                                                    battery_voltage=24,
                                                    time=timezone.now(),
                                                    AC_input=0.0,
                                                    AC_output=15.0,
                                                    AC_Load_in=0.0,
                                                    AC_Load_out=-0.7)

        self.new_rmc_status = RMC_status.objects.create(site=self.site,
                                                        ip_address='127.0.0.1',
                                                        minutes_last_contact=1,
                                                        signal_strength=27,
                                                        data_sent_24h=12,
                                                        time=datetime.now())


        self.client = Client()


    @override_settings(DEBUG=True)
    def test_alert_fires_and_reported(self):
        """
        Test if the alerts objects are fired and saved.
        and also if the alert is notified to mails, sms and slack.
        """
        alerts_created = Sesh_Alert.objects.filter(site=self.site)
        self.assertEqual(alerts_created.count(),4)

        alerts_mail_sent = alerts_created.filter(emailSent=True)
        self.assertEqual(alerts_mail_sent.count(),4)


        # test_sent_sms, sms are not sent where debug is false
        alert_sms_sent = Sesh_Alert.objects.filter(smsSent=True)
        if settings.DEBUG:
            self.assertEqual(alert_sms_sent.count(), 0)
        else:
            self.assertEqual(alert_sms_sent.count(), 1)

        #test_slack
        alert_slack_sent = Sesh_Alert.objects.filter(slackSent=True)
        self.assertEqual(alert_slack_sent.count(), 4)


    def test_alert_display(self):
        """
        Test the display of alerts to the user
        """
        self.client.login(username='patrick', password='test.test.test')
        alerts = Sesh_Alert.objects.all()
        print "#####################"
        print alerts
        for alert in alerts:
            print alert.id
        response = self.client.post('/get-alert-data/',{'alertId':'1'})
        self.assertEqual(response.status_code, 200)


        #test_get_alerts_notifications
        response = self.client.post('/notifications/',{})
        self.assertEqual(response.status_code, 200)

        # Test the display of the status card data
        response = self.client.post('/get-latest-bom-data/',{"siteId": 1})
        self.assertEqual(response.status_code, 200)



    def test_alert_silencing(self):
        """
        Testing the silencing of alerts
        """
        self.client.login(username="patrick", password="test.test.test")
        response = self.client.post('/silence-alert/',{'alert_id':'1'})

        self.assertEqual(response.status_code, 200)
        silenced_alert = Sesh_Alert.objects.filter(id=1).first()
        self.assertEqual(silenced_alert.isSilence, True)



    @override_settings(DEBUG=True)
    def test_alert_autosilencing(self):
        """
        Test if alerts are silencing correctly
        """
        alert.alert_status_check()
        unsilenced_alerts = Sesh_Alert.objects.filter(isSilence=False)
        self.assertEqual(unsilenced_alerts.count(), 0)
