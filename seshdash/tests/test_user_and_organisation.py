from django.test import TestCase, Client
from django.core.urlresolvers import reverse

from seshdash.models import Sesh_User, Sesh_Organisation


class UserOrganisationTestCase(TestCase):
    """
    Tests the functionality of sesh users
    and the sesh organisations
    """
    def setUp(self):
        """
        Initializing the db
        """
        self.test_organisation = Sesh_Organisation.objects.create(name='test_organisation', slack_token='')
        self.test_sesh_user_not_admin = Sesh_User.objects.create_user(username='test_user_not_admin', 
                                                            password='test.test.test',
                                                            email='test@test.test',
                                                            organisation=self.test_organisation
                                                       )

        self.test_user_admin = Sesh_User.objects.create_user(username='test_user_admin',
                                                             password='test.test.test',
                                                             email='test@test.test',
                                                             organisation=self.test_organisation,
                                                             is_org_admin=True
                                                       )

        self.client = Client()

    def test_display_users(self):
        """
        Testing the display of the user editing 
        page
        """
        self.client.login(username='test_user_admin', password='test.test.test')
        response = self.client.get(reverse('manage_org_users'))
        self.assertEqual(response.status_code, 200)

    def test_add_user(self):
        """
        TestCase for adding a sesh user
        """
        data = {
            'username':'test_sesh_user_two',
            'password':'test.test.test',
            'email':'test@test.test',
        }

        self.client.login(username='test_user_not_admin', password='test.test.test')
        # Testing unauthorized user
        response = self.client.post(reverse('add_sesh_user'), data)
        self.assertEqual(response.status_code, 403)


        # Testing authorized user
        self.client.login(username='test_user_admin', password='test.test.test') 
        response = self.client.post(reverse('add_sesh_user'), data)
        self.assertEqual(response.status_code, 302)
        # asserting the results of the operation, the number also contains the AnonymousUser which is autogenerated
        self.assertEqual(Sesh_User.objects.all().count(), 4)

 
    def test_delete_sesh_user(self):
        """
        Testing the deleting of a sesh user
        """
        self.client.login(username='test_user_admin', password='test.test.test')
        
        response = self.client.get(reverse('delete_sesh_user', args=[self.test_sesh_user_not_admin.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Sesh_User.objects.all().count(), 2)


    def test_edit_sesh_user(self):
        """
        Testing the editing of a seshuser
        """
        data = {
            'username': 'test_user_not_admin',
            'email':'testing@testing.testing',
            'password': 'test.test.test',
         }
 
        # Testing unauthorize user
        self.client.login(username='test_user_not_admin', password='test.test.test')
        response = self.client.post(reverse('edit_sesh_user', args=[self.test_sesh_user_not_admin.id]))
        self.assertEqual(response.status_code, 403)

        # Testing authorized user
        self.client.login(username='test_user_admin', password='test.test.test')
        response = self.client.post(reverse('edit_sesh_user', args=[self.test_sesh_user_not_admin.id]), data)
        user = Sesh_User.objects.filter(id=self.test_sesh_user_not_admin.id).first()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(user.email, 'testing@testing.testing')
      
 
