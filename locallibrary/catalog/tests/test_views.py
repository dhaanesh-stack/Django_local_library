from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from catalog.models import Author
import datetime

class AuthorCreateViewTest(TestCase):
    """Test case for the AuthorCreate view."""

    def setUp(self):
        # Create a user
        self.test_user = User.objects.create_user(
            username='test_user', password='some_password'
        )

        # Assign 'add_author' permission
        content_type_author = ContentType.objects.get_for_model(Author)
        perm_add_author = Permission.objects.get(
            codename="add_author",
            content_type=content_type_author,
        )
        self.test_user.user_permissions.add(perm_add_author)
        self.test_user.save()

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('author-create'))
        self.assertRedirects(response, '/accounts/login/?next=/catalog/author/create/')

    def test_logged_in_with_permission(self):
        self.client.login(username='test_user', password='some_password')
        response = self.client.get(reverse('author-create'))

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/author_form.html')

        # Check initial value
        self.assertEqual(
            response.context['form'].initial['date_of_death'], '11/11/2023'
        )

    def test_create_author_post(self):
        self.client.login(username='test_user', password='some_password')
        response = self.client.post(
            reverse('author-create'),
            {
                'first_name': 'John',
                'last_name': 'Doe',
                'date_of_birth': '1970-01-01',
                'date_of_death': '2023-11-11',
            }
        )

        # Should redirect to detail page of new author
        self.assertEqual(response.status_code, 302)

        # Check object was created
        author = Author.objects.last()
        self.assertEqual(author.first_name, 'John')
        self.assertEqual(author.last_name, 'Doe')
