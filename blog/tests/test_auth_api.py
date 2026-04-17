from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from blog.models import CustomUser


class RegisterAPITestCase(APITestCase):
    """Тесты для эндпоинта регистрации пользователя"""

    def test_register_success(self):
        """Тест успешной регистрации нового пользователя"""
        url = reverse('register')
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!'
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomUser.objects.count(), 1)
        self.assertEqual(CustomUser.objects.get().username, 'testuser')
        self.assertEqual(response.data['username'], 'testuser')

    def test_register_password_mismatch(self):
        """Тест регистрации с несовпадающими паролями"""
        url = reverse('register')
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'password_confirm': 'DifferentPass!'
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(CustomUser.objects.count(), 0)

    def test_register_missing_fields(self):
        """Тест регистрации без обязательных полей"""
        url = reverse('register')
        data = {
            'username': 'testuser',
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(CustomUser.objects.count(), 0)

    def test_register_duplicate_username(self):
        """Тест регистрации с существующим именем пользователя"""
        url = reverse('register')
        CustomUser.objects.create_user(username='testuser', email='test@example.com', password='TestPass123!')

        data = {
            'username': 'testuser',
            'email': 'test2@example.com',
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!'
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(CustomUser.objects.count(), 1)


class LoginAPITestCase(APITestCase):
    """Тесты для эндпоинта входа"""

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        self.url = reverse('login')

    def test_login_success(self):
        """Тест успешного входа"""
        data = {
            'username': 'testuser',
            'password': 'TestPass123!'
        }
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('detail', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'testuser')

    def test_login_wrong_password(self):
        """Тест входа с неверным паролем"""
        data = {
            'username': 'testuser',
            'password': 'WrongPassword!'
        }
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_nonexistent_user(self):
        """Тест входа несуществующего пользователя"""
        data = {
            'username': 'nonexistent',
            'password': 'TestPass123!'
        }
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_missing_fields(self):
        """Тест входа без обязательных полей"""
        data = {
            'username': 'testuser'
        }
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def tearDown(self):
        self.user.delete()

        super().tearDown()


class LogoutAPITestCase(APITestCase):
    """Тесты для эндпоинта выхода"""

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        self.url = reverse('logout')

    def test_logout_authenticated(self):
        """Тест выхода авторизованного пользователя"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('detail', response.data)

    def test_logout_unauthenticated(self):
        """Тест выхода неавторизованного пользователя"""
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def tearDown(self):
        self.user.delete()

        super().tearDown()


class UserProfileAPITestCase(APITestCase):
    """Тесты для эндпоинта профиля пользователя"""

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!',
            first_name='Test',
            last_name='User'
        )
        self.url = reverse('profile')

    def test_get_profile_authenticated(self):
        """Тест получения профиля авторизованного пользователя"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['first_name'], 'Test')

    def test_get_profile_unauthenticated(self):
        """Тест получения профиля неавторизованного пользователя"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_profile_put(self):
        """Тест полного обновления профиля"""
        self.client.force_authenticate(user=self.user)
        data = {
            'username': 'testuser',
            'first_name': 'Updated',
            'last_name': 'Name',
            'bio': 'New bio',
            'github_username': 'updateduser'
        }
        response = self.client.put(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.bio, 'New bio')

    def test_update_profile_patch(self):
        """Тест частичного обновления профиля"""
        self.client.force_authenticate(user=self.user)
        data = {'bio': 'Updated bio'}
        response = self.client.patch(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.bio, 'Updated bio')
        self.assertEqual(self.user.first_name, 'Test')

    def test_update_profile_unauthenticated(self):
        """Тест обновления профиля неавторизованного пользователя"""
        data = {'bio': 'Bio'}
        response = self.client.patch(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)