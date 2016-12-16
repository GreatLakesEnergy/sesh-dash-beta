# Testing
from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.utils import timezone

from geoposition import Geoposition

from seshdash.data.db.influx import Influx
from seshdash.models import Sesh_Site

class DataAnalysisTestCase(TestCase):
    """
    Testing the functions that help in analysing and presenting
    the Data sesh collects
    """

    def setUp(self):
        """
        Initializing
        """
        self.client = Client()

        self.location = Geoposition(52.5,24.3)

        # Setup Influx
        self._influx_db_name = 'test_db'
        self.i = Influx(database=self._influx_db_name)

        try:
            self.i.create_database(self._influx_db_name)
        except:
           self.i.delete_database(self._influx_db_name)
           sleep(1)
           self.i.create_database(self._influx_db_name)
           pass

        self.site = Sesh_Site.objects.create(site_name=u"Test site",
                                             comission_date=timezone.datetime(2015, 12, 11, 22, 0),
                                             location_city=u"kigali",
                                             location_country=u"rwanda",
                                             installed_kw=123.0,
                                             position=self.location,
                                             system_voltage=24,
                                             number_of_panels=12,
                                             vrm_site_id=213,
                                             battery_bank_capacity=12321,
                                             has_genset=True,
                                             has_grid=True,
                                            )   
    
   
    def test_get_csv_data(self):
        """
        Testing the functions that return csv files
        for a given measuremnt
        """
        data = {
            'measurement': 'battery_voltage',
            'start-time': '2015-01-01',
            'end-time': '2017-01-01',
            'site-name': self.site.site_name
        }

        response = self.client.post(reverse('export-csv-data'), data) 
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Type'), 'text/csv')
