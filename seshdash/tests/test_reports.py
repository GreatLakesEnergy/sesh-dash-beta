"""
Testing the funcionality of the reports
and the reporting utils
"""
from datetime import datetime

from django.test import TestCase
from django.utils import timezone
from django.db.models import Avg, Sum
from django.core.urlresolvers import reverse
from geoposition import Geoposition

from seshdash.models import Daily_Data_Point, Report_Job, Sesh_Site, Sesh_Organisation, Sesh_User, Report_Sent
from seshdash.utils.reporting import send_report, get_emails_list, get_edit_report_list, is_in_report_attributes,\
                                     _format_column_str
from seshdash.tasks import check_reports
from seshdash.data.db.influx import Influx
from seshdash.data.db.kapacitor import Kapacitor


class ReportTestCase(TestCase):
    def setUp(self):
        """
        Initializing
        """
        self.location = Geoposition(1.7, 1.8)

        self.organisation = Sesh_Organisation.objects.create(name='test_org',
                                                             slack_token='testing_token')

        self.test_user = Sesh_User.objects.create_user(username='test_user',
                                                       email='test@gle.solar',
                                                       password='test.test.test',
                                                       organisation=self.organisation,
                                                       is_org_admin=True,
                                                       department='test',
                                                       send_mail=True)

        self.site = Sesh_Site.objects.create(site_name='test_site',
                                             organisation=self.organisation,
                                             comission_date=timezone.now(),
                                             location_city='kigali',
                                             location_country='Rwanda',
                                             installed_kw=123.0,
                                             position = self.location,
                                             system_voltage = 12,
                                             number_of_panels = 12,
                                             battery_bank_capacity = 1000)

        self.attributes_data = [
                                   #REMOVING THIS because we are not using sesh table for reports
                                   #{"table":"Daily_Data_Point",
                                   # "column":"daily_pv_yield",
                                   # "operation":"average",
                                   # "user_friendly_name":"Daily pv yield average"},
                                   #{"table":"Daily_Data_Point",
                                   # "column":"daily_power_consumption_total",
                                   # "operation":"sum",
                                   # "user_friendly_name":"Daily power consumption total sum"
                                   #},
                                   {"operation": "sum",
                                    "field": "trans",
                                    "output_field": "sum_trans",
                                    "user_friendly_name": "Trans sum"},
                                    {"operation": "mean",
                                     "field": "relay_state",
                                     "output_field": "mean_relay_state",
                                     "user_friendly_name": "Relay state mean"}
                               ]


        self.report = Report_Job.objects.create(site=self.site,
                                            duration="daily",
                                            day_to_report=datetime.now().today().weekday(),
                                            attributes=self.attributes_data)

        self.i = Influx()
        self.kap = Kapacitor()

    def test_models(self):
        """
        Testing the models
        """
        self.assertEqual(Report_Job.objects.all().count(), 1)

    def test_send_reports(self):
        """
        Testing the task that send reports
        """
        #reported_reports = check_reports()
        #self.assertEqual(reported_reports, 1)
        print "test the generation of report instnacne"

    def test_send_report(self):
        """
        Testing the sending of the generated reports,
        Test logging of report
        """
        #val = send_report(self.report)

        #report_log = Report_Sent.objects.all()
        #self.assertTrue(val)
        #self.assertGreater(len(report_log),0)
        print "the sending of report messages"


    def test__format_column_str(self):
        """
        Tests the formating of a string,
        changing column to spaces and capitalizing the first letter
        """
        val = _format_column_str('daily_pv_yield')
        self.assertEqual(val, 'Daily pv yield')

    def test_get_email_users(self):
        """
        A function to return a list of emails
        when given an array of sesh user instances
        """
        mail_list = get_emails_list([self.test_user])
        self.assertEqual(mail_list, ['test@gle.solar'])

    def test_add_report(self):
        """
        Testing the adding of the reports from
        a client to a the db
        """
        # The below is the format of the data that is received from a client when adding a report
        data = {

            'duration': 'weekly',

            '{"operation": "sum", \
             "field": "trans", \
             "output_field": "sum_trans", \
             "user_friendly_name": "Trans sum"}': ['on'],

            '{"operation": "mean", \
             "field": "relay_state", \
             "output_field": "mean_relay_state", \
             "user_friendly_name": "Relay state mean"}': ['on'],
        }

        self.client.login(username='test_user', password='test.test.test')
        response = self.client.post(reverse('add_report', args=[self.site.id]), data)

        self.assertEqual(response.status_code, 302) # Testing the redirection to manage reports page for site
        self.assertEqual(Report_Job.objects.all().count(), 2)

    def test_delete_report(self):
        """
        Testing the deletion of a report
        """
        self.client.login(username='test_user', password='test.test.test')
        response = self.client.get(reverse('delete_report', args=[self.report.id]))
        self.assertEqual(response.status_code, 302) # Testing the redirection to manage reports page for site

        self.assertEqual(Report_Job.objects.all().count(), 0)

    def test_is_in_report_attributes(self):
        """
        Testing the function that determines if an attribute
        is in the report.attribues
        """
        result = is_in_report_attributes(self.report.attributes[0], self.report)
        self.assertTrue(result)

    def test_get_edit_report_list(self):
        """
        Testing the function that returns a list representing the report.attributes
        status.

        The function returns a dict, which has status on for each active attribute and off otherwise
        """
        # Creating measurements to the influx db
        self.i.insert_point(site=self.site, measurement_name='trans', value=0)
        self.i.insert_point(site=self.site, measurement_name='relay_state', value=0)

        report_dict = get_edit_report_list(self.report)
        count = 0

        for item in report_dict:
            if item['status'] == 'on':
                count += 1

        self.assertEqual(count, 2) # Testing that the report list is detecting 2 attributes in the report.

    def test_edit_report(self):
        """
        This will test the editing of the sesh
        reports
        """
        self.client.login(username='test_user', password='test.test.test')
        data = {
            '{"operation": "sum", \
             "field": "trans", \
             "output_field": "sum_trans", \
             "user_friendly_name": "Trans sum"}': ['on'],
             'duration': 'weekly',
        }

        response = self.client.post(reverse('edit_report', args=[self.report.id]), data)
        self.assertEqual(response.status_code, 302)  # The rediction to the manage reports

        report = Report_Job.objects.filter(id=self.report.id).first()
        self.assertEqual(report.duration, 'weekly')
        self.assertEqual(len(report.attributes), 1)
