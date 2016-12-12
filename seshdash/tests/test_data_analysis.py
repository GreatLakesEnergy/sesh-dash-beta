# Testing
from django.test import TestCase, Client
from django.core.urlresolvers  import reverse


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

   
    def test_get_csv_data(self):
        """
        Testing the functions that return csv files
        for a given measuremnt
        """
        response = self.client.post(reverse('measurement_data_csv'), {'measurement':'battery_voltage'}) 
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Type'), 'text/csv')
