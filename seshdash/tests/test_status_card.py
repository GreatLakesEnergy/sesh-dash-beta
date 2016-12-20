from django.test import TestCase, Client
from django.utils import timezone
from django.core.urlresolvers import reverse

from guardian.shortcuts import assign_perm

from seshdash.data.db.influx import Influx
from seshdash.models import Sesh_User, Sesh_Site, Status_Card, Sesh_Organisation

from geoposition import Geoposition

class StatusCardTestCase(TestCase):
    """
    Testing the status card
    """
    def setUp(self):
        """
        Initializing
        """
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

 
        self.client = Client()
        self.organisation = Sesh_Organisation.objects.create(name='test_organisation')
                                                             
        self.user = Sesh_User.objects.create_user(username='test_user',
                                             password='test.test.test', 
                                             email='test@gle.solar',
                                             organisation=self.organisation
                                             )
        self.location = Geoposition(1, 4)
        self.site = Sesh_Site.objects.create(site_name='test_site', 
                                             organisation=self.organisation,
                                             comission_date=timezone.now(),
                                             location_city='',
                                             location_country='',
                                             installed_kw='13', 
                                             position=self.location,
                                             system_voltage=24,
                                             number_of_panels=12,
                                             battery_bank_capacity=1200)


        self.status_card = Status_Card.objects.create(row1='AC_Load_in',
                                                      row2='AC_Load_out',
                                                      row3='AC_Voltage_in',
                                                      row4='AC_Voltage_out') 

        self.site.status_card = self.status_card
        self.site.save()

        assign_perm('view_Sesh_Site', self.user, self.site)

    def test_edit_status_card(self):
        """
        Testing the editing of a status card
        """
        data = {
            'row1': 'battery_voltage',
            'row2': 'AC_Load_in',
            'row3': 'AC_Voltage_in',
            'row4': 'AC_Voltage_out'
        }

        # Testing for a user that is not an admin
        self.client.login(username='test_user', password='test.test.test')
        response = self.client.post(reverse('edit_status_card', args=[self.site.id]), data)
        self.assertEqual(response.status_code, 400)


        # Testing if the changes have been applied
        self.user.is_org_admin = True
        self.user.save()
        response = self.client.post(reverse('edit_status_card', args=[self.site.id]), data)
        self.assertRedirects(response, reverse('index', args=[self.site.id]))

        # Testing if the changes have been applied
        status_card = Status_Card.objects.filter(id=self.status_card.id).first()
        self.assertEqual(status_card.row1, 'battery_voltage')
      


