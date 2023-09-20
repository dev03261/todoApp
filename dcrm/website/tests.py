from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import TODO
from .forms import TODOForm
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm


class LoginViewTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpassword')
        self.client = Client()  # Create a new client instance for each test

    def test_login_get(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], AuthenticationForm)

    def test_login_post_valid(self):
        post_data = {
            'username': 'testuser',
            'password': 'testpassword',
        }
        response = self.client.post(reverse('login'), data=post_data)
        self.assertRedirects(response, reverse('home'))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_post_invalid(self):
        post_data = {
            'username': 'testuser',
            'password': 'wrongpassword',
        }
        response = self.client.post(reverse('login'), data=post_data)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], AuthenticationForm)
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class SignInViewTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpassword')
        self.client = Client()  # Create a new client instance for each test

    def test_signUn_get(self):
        response = self.client.get(reverse('signUp'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], UserCreationForm)

    def test_sign_up_post_valid(self):
        post_data = {
            'username': 'newuser',
            'password1': 'testpassword',
            'password2': 'testpassword',
        }

        response = self.client.post(reverse('signUp'), data=post_data)
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_sign_up_post_invalid(self):
        post_data = {
            'username': '',  # Invalid: Username is required
            'password1': 'testpassword',
            'password2': 'testpassword',
        }

        response = self.client.post(reverse('signUp'), data=post_data)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], UserCreationForm)
        self.assertFalse(User.objects.filter(username='').exists())


class HomeViewTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpassword')

    def test_home_authenticated_user(self):
        self.client.login(username='testuser', password='testpassword')
        todo = TODO.objects.create(
            user=self.user, title='Test Task', status='todo')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertIsInstance(response.context['form'], TODOForm)
        self.assertEqual(response.context['todos'].first(), todo)

    def test_home_unauthenticated_user(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))


class DeleteTodoViewTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpassword')
        self.todo = TODO.objects.create(
            user=self.user, title='Test Task', status='todo')

    def test_delete_todo_authenticated_user(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('delete_todo', args=[self.todo.id]))
        self.assertRedirects(response, reverse('home'))
        self.assertFalse(TODO.objects.filter(pk=self.todo.id).exists())

    def test_delete_todo_unauthenticated_user(self):
        response = self.client.get(reverse('delete_todo', args=[self.todo.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(TODO.objects.filter(pk=self.todo.id).exists())


class ChangeStatusTodoViewTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpassword')
        self.todo = TODO.objects.create(
            user=self.user, title='Test Task', status='todo')

    def test_change_todo_authenticated_user(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(
            reverse('mark-as-done', args=[self.todo.id]))
        self.assertRedirects(response, reverse('home'))
        updated_todo = TODO.objects.get(pk=self.todo.id)
        self.assertEqual(updated_todo.status, 'C')

    def test_change_todo_unauthenticated_user(self):
        response = self.client.get(
            reverse('mark-as-done', args=[self.todo.id]))
        self.assertEqual(response.status_code, 302)
        updated_todo = TODO.objects.get(pk=self.todo.id)
        self.assertEqual(updated_todo.status, 'C')


class ChangeDetailTodoViewTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser', password='testpassword')

    def test_edit_details_empty_fields(self):
        self.client.login(username='testuser', password='testpassword')
        todo = TODO.objects.create(
            user=self.user, title='Test Task', status='todo')
        post_data = {
            'title': '',
            'status': 'done',
        }
        response = self.client.post(
            reverse('edit-details', args=[todo.id, 'done']), data=post_data)
        self.assertEqual(response.status_code, 200)

    def test_edit_details_authenticated_user(self):
        self.client.login(username='testuser', password='testpassword')
        todo = TODO.objects.create(
            user=self.user, title='Test Task', status='todo')
        post_data = {
            'title': 'Updated Task Title',
            'priority': '1',
        }
        response = self.client.post(
            reverse('edit-details', args=[todo.id, 'done']), data=post_data)
        self.assertRedirects(response, reverse('home'))
        updated_todo = TODO.objects.get(pk=todo.id)
        self.assertEqual(updated_todo.title, 'Updated Task Title')
        self.assertEqual(updated_todo.priority, '1')


class SignOutTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="testuser", password="testpassword"
        )
        self.user.save()

    def test_sign_out(self):
        self.client.login(username="testuser", password="testpassword")
        self.assertTrue(self.user.is_authenticated)
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
