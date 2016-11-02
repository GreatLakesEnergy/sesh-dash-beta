"""
Testing the funcionality of the reports
and the reporting utils
"""
from django.test import TestCase
from django.utils import timezone
from geoposition import Geoposition

from seshdash.models import Daily_Data_Point, Report, Sesh_Site
from seshdash.utils.reporting import generate_report

class ReportTestCase(TestCase):
    def setUp(self):
        """
        Initializing
        """
        self.location = Geoposition(1.7, 1.8)
        self.site = Sesh_Site.objects.create(site_name='test_site', 
                                             comission_date=timezone.now(),
                                             location_city='kigali',
                                             location_country='Rwanda',
                                             installed_kw=123.0,
                                             position = self.location,
                                             system_voltage = 12,
                                             number_of_panels = 12,
                                             battery_bank_capacity = 1000)

        self.attributes_data = [
                                   {"table":"Daily_Data_Point", "column":"daily_pv_yield", "operation":"average"},
                                   {"table":"Daily_Data_Point", "column":"daily_power_consumption_total", "operation":"sum"},
                               ]

        self.daily_data_point_one = Daily_Data_Point.objects.create(
                                            site = self.site,
                                            date = timezone.now(),
                                            daily_pv_yield = 10,
                                            daily_power_consumption_total = 10,
                                    )

        self.daily_data_point_two = Daily_Data_Point.objects.create(
                                            site = self.site,
                                            date = timezone.now(),
                                            daily_pv_yield = 10,
                                            daily_power_consumption_total = 10,
                                    )

        self.report = Report.objects.create(site=self.site,
                                            duration="daily",
                                            day_to_report=1,
                                            attributes=self.attributes_data)

        
    def test_models(self):
        """
        Testing the models
        """
        self.assertEqual(Report.objects.all().count(), 1)     

    def test_generate_report(self):
        """
        Testing the util that generates the report dict
        """
        results = generate_report(self.report)
        # Asserting if the aggregations are correct
        self.assertEqual(results['daily_pv_yield__avg'], 10)
        self.assertEqual(results['daily_power_consumption_total__sum'], 20)
