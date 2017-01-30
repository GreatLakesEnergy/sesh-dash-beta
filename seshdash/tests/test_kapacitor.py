# Testing
from django.test import TestCase, Client
from django.test.utils import override_settings

# APP Models
from seshdash.models import Sesh_Alert, Alert_Rule, Sesh_Site,VRM_Account, BoM_Data_Point as Data_Point, Daily_Data_Point, Sesh_User

# django Time related
from django.utils import timezone
from time import sleep
from datetime import timedelta
import pytz

#Helper Functions
from django.forms.models import model_to_dict
from django.core import mail
from django.template.loader import get_template

#Security
from guardian.shortcuts import assign_perm
from geoposition import Geoposition

#Data generations
from data_generation import get_random_int, get_random_binary, get_random_interval, generate_date_array, get_random_float

# Debug
from django.forms.models import model_to_dict

# To Test
from seshdash.utils.time_utils import get_time_interval_array
from seshdash.data.db.kapacitor import Kapacitor
from seshdash.data.db.influx import  Influx
from django.conf import settings
from seshdash.tasks import get_aggregate_daily_data
from seshdash.tests.data_generation import create_test_data


# This test case written to test alerting module.
# It aims to test if the system sends an email and creates an Sesh_Alert object when an alert is triggered.
class KapacitorTestCase(TestCase):

    def setUp(self):

        # Need this to create a Site
        self.VRM = VRM_Account.objects.create(vrm_user_id='asd@asd.com',vrm_password="asd")

        # Setup Influx
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

        # Setup Kapacitor
        self.kap = Kapacitor()
        self.template_id = 'test_template'
        self.task_id = 'test_task'
        self.dj_template_name = 'alert_template'


        self.dbrps = [{'db': self._influx_db_name, 'rp':'autogen' }]


        self.location = Geoposition(52.5,24.3)
        dt = timezone.make_aware(timezone.datetime(2015, 12, 11, 22, 0))

        self.site = Sesh_Site.objects.create(site_name=u"Test_aggregate",
                                             comission_date = dt,
                                             location_city = u"kigali",
                                             location_country=u"rwanda",
                                             vrm_account = self.VRM,
                                             installed_kw=123.0,
                                             position=self.location,
                                             system_voltage=12,
                                             number_of_panels=12,
                                             vrm_site_id=213,
                                             battery_bank_capacity=12321,
                                             has_genset=True,
                                             has_grid=True)

        #self.no_points = create_test_data(self.site,
       #                                 start = self.site.comission_date,
       #                                 end = dt + timedelta( hours = 48),
       #                                 interval = 30,
       #                                 random = False)

        #create test user
        self.test_user = Sesh_User.objects.create_user("john doe","alp@gle.solar","asdasd12345")
        #assign a user to the sites
        assign_perm("view_Sesh_Site",self.test_user,self.site)


    def tearDown(self):
        self.i.delete_database(self._influx_db_name)
        self.kap.delete_template(self.template_id)
        self.kap.delete_task(self.task_id)
        pass

    @override_settings(INFLUX_DB='test_db')
    def test_template_creation(self):
        """
        Test creating template in kapacitor
        """


        temp_script = """
        // Which measurement to consume
        var measurement string
        // Optional where filter
        var where_filter = lambda: TRUE
        // Optional list of group by dimensions
        var groups = [*]
        // Which field to process
        var field string
        // Warning criteria, has access to 'mean' field
        var warn lambda
        // Critical criteria, has access to 'mean' field
        var crit lambda
        // How much data to window
        var window = 5m
        // The slack channel for alerts
        var slack_channel = '#alerts'

        stream
            |from()
                .measurement(measurement)
                .where(where_filter)
                .groupBy(groups)
            |window()
                .period(window)
                .every(window)
            |mean(field)
            |alert()
                 .warn(warn)
                 .crit(crit)
                 .slack()
                 .channel(slack_channel)

        """
        temp_id = self.template_id
        temp_type = 'stream'

        # Create template
        temp = self.kap.create_template(temp_id, temp_type, temp_script)
        self.assertTrue(temp.has_key('vars'))

        # Verify template creation
        temp_res = self.kap.get_template(temp_id)
        self.assertTrue(temp_res.has_key('vars'))

        # List template
        temp_res = self.kap.list_templates()
        self.assertTrue(temp_res.has_key('templates'))

        # Update Template

        temp_script = """
        // Which measurement to consume
        var measurement = 'cpu'
        // Optional where filter
        var where_filter = lambda: TRUE
        // Optional list of group by dimensions
        var groups = [*]
        // Which field to process
        var field string
        // Warning criteria, has access to 'mean' field
        var warn lambda
        // Critical criteria, has access to 'mean' field
        var crit lambda
        // How much data to window
        var window = 5m
        // The slack channel for alerts
        var slack_channel = '#alerts'

        stream
            |from()
                .measurement(measurement)
                .where(where_filter)
                .groupBy(groups)
            |window()
                .period(window)
                .every(window)
            |mean(field)
            |alert()
                 .warn(warn)
                 .crit(crit)
                 .slack()
                 .channel(slack_channel)

        """
        temp_res = self.kap.update_template(temp_id, temp_script)

        # Delete template
        self.kap.delete_template(self.template_id)

    def test_task_creation(self):
        """
        Create a task and check if it actually causes an alert to trigger
        """


        temp_script = """
                    stream
                        |from()
                            .measurement('cpu')
                        |alert()
                            .crit(lambda: "value" <  70)
                            .log('/tmp/alerts.log')
                        """

        temp_id = self.template_id
        task_id = self.task_id


        # Create task
        temp = self.kap.create_task(task_id, dbrps=self.dbrps, script=temp_script, task_type='stream')
        self.assertEqual(temp['status'],'enabled')
        sleep(20)

        for i in reversed(range(0,5)):
            sleep(1)
            dp_dict = {'cpu': i}
            self.i.send_object_measurements(dp_dict, tags={"site_name":"test_site"}, database=self._influx_db_name)
        temp = self.kap.get_task(task_id)

        self.assertGreater(temp['stats']['node-stats']['alert2']['alerts_triggered'], 0)

    def test_task_dj_template(self):
        """
        test task creation with django templates
        """

        template =  get_template('seshdash/kapacitor_tasks/%s.tick'%self.dj_template_name)

        alert_id = self.task_id
        alert_info ={
                'field': 'cpu',
                'where_filter_lambda' : 'lambda: TRUE',
                'error_lambda' : 'lambda: \"value\" < 30',
                'time_window' : '5m',
                'slack_channel' : '#alerts'
                }


        rendered_alert = template.render(alert_info)
        result = self.kap.create_task(alert_id, dbrps= self.dbrps, script=rendered_alert)
        self.assertEquals(result['status'], 'enabled')

    def test_set_task_status(self):
        """
        Testing the function that updates status
        of tasks
        """ 
        script = """
                    stream
                        |from()
                            .measurement('cpu')
                        |alert()
                            .crit(lambda: "value" <  70)
                            .log('/tmp/alerts.log')
                        """

        task = self.kap.create_task('test_task', script, status='enabled')
        self.kap.set_task_status('test_task', 'disabled')

        # asserting
        task = self.kap.get_task('test_task')
        self.assertEqual(task['status'], 'disabled')
        





