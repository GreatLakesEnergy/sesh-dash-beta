from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.utils import  timezone
from django.contrib.auth.models import User
from geoposition import Geoposition
from time import sleep

from seshdash.models import Alert_Rule, Sesh_Site, Sesh_User
from seshdash.data.db.influx import Influx

class TestAlertRules(TestCase):
    """
    Testing the alert rules options in the 
    settings
    """

    def setUp(self):
        """
        Setting up the db
        """

        # Adding an influx database used by the quick_status_icons functions used on the pages to render
        self.influx_db_name = 'test_db'
        self.i = Influx(database=self.influx_db_name)

        try:
            self.i.create_database(self.influx_db_name)
        except:
            # Database already exist
            self.i.delete_database(self.influx_db_name)
            sleep(1)
            self.i.create_database(self.influx_db_name)
            pass

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

        self.alert_rule = Alert_Rule.objects.create(
                        site=self.site,
                        check_field='battery_voltage',
                        operator='lt',
                        value='0',
                    )


        self.sesh_user = Sesh_User.objects.create_superuser(username='test_user',
                                                             email='test@sesh.sesh',
                                                             password='test.test.test',
                                                             on_call=False,
                                                             send_sms=False,
                                                             send_mail=False)     
           
 
    def test_settings_alert_rules_page(self):
        """
        Testing if the page is 
        being rednered correctl
        """
        self.client.login(username='test_user', password='test.test.test')
        response = self.client.get(reverse('manage_alert_rules'))
        self.assertEqual(response.status_code, 200)

    def test_add_alert_rule(self):
        """
        Testing the addition of alert rules
        """
        data = {
                'check_field': 'battery_voltage',
                'operator': 'lt',
                'value': '20',
            }


        self.client.login(username='test_user', password='test.test.test')
        
        # Testing the creation of an alert rulses
        response = self.client.post(reverse('site_alert_rules', args=[self.site.id]), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Alert_Rule.objects.filter(site=self.site).count(), 2)

    def test_edit_alert_rule(self):
        """
        Testing the editing of an alert rule 
        """
        data = {
                'check_field': 'battery_voltage',
                'operator': 'gt',
                'value': '100',
            }

        self.client.login(username='test_user', password='test.test.test')

        response = self.client.post(reverse('edit_alert_rule', args=[self.alert_rule.id]), data)

        # Testing the success of editing an alert rule
        self.assertEqual(response.status_code, 302)
        alert_rule = Alert_Rule.objects.filter(id=self.alert_rule.id).first() # Need to query the database again to get updated version
        self.assertEqual(alert_rule.operator, 'gt')
        self.assertEqual(alert_rule.value, 100)


    def test_delete_alert_rule(self):
        """
        Testing the deletion of alert rules
        """
        self.client.login(username='test_user', password='test.test.test')

        response = self.client.get(reverse('delete_alert_rule', args=[self.alert_rule.id]))

        # Testing the success of deleting an alert rule
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Alert_Rule.objects.all().count(), 0)

        def test_user_notifications(self):
                """
                Testing the user notifications
                """
                self.client.login(username='test_user', password='test.test.test')
                
                data = {
                          u'form-MAX_NUM_FORMS': [u'1000'],
                          u'form-INITIAL_FORMS': [u'3'],
                          u'form-TOTAL_FORMS': [u'1'],
                          u'form-0-send_sms': [u'on'],
                          u'form-0-on_call': [u'on'],
                          u'form-0-id': [u'1'],
                          u'form-MIN_NUM_FORMS': [u'0']
                }
               
                response = self.client.post(reverse('user_notifications'), data)
                 
                # Asserting the correctness of the response and the result of the post
                self.assertEqual(response.status_code, 302)
                user = Sesh_User.objects.filter(user=self.user).first()
                self.assertEqual(user.on_call, True)
                self.assertEqual(user.send_sms, True)
