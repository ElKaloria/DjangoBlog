from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from blog.models import Post, Like, CustomUser


class LikeCreateAPITestCase(APITestCase):
    """Тесты для создания лайков"""

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser', email='test@example.com', password='Pass123!'
        )
        self.other_user = CustomUser.objects.create_user(
            username='otheruser', email='other@example.com', password='Pass123!'
        )
        self.post = Post.objects.create(
            title='Test Post',
            content='Test content',
            author=self.user
        )
        self.url = reverse('like-create-like', kwargs={'post_pk': self.post.pk})

    def test_create_like_authenticated(self):
        """Тест создания лайка авторизованным пользователем"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Like.objects.count(), 1)
        self.assertIn('detail', response.data)

    def test_create_like_unauthenticated(self):
        """Тест создания лайка неавторизованным пользователем"""
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_duplicate_like(self):
        """Тест создания дублирующегося лайка"""
        self.client.force_authenticate(user=self.user)
        Like.objects.create(user=self.user, post=self.post)
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Like.objects.count(), 1)
        self.assertIn('detail', response.data)

    def test_create_like_for_nonexistent_post(self):
        """Тест лайка несуществующего поста"""
        self.client.force_authenticate(user=self.user)
        url = reverse('like-create-like', kwargs={'post_pk': 9999})
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class LikeDeleteAPITestCase(APITestCase):
    """Тесты для удаления лайков"""

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser', email='test@example.com', password='Pass123!'
        )
        self.other_user = CustomUser.objects.create_user(
            username='otheruser', email='other@example.com', password='Pass123!'
        )
        self.post = Post.objects.create(
            title='Test Post',
            content='Test content',
            author=self.user
        )
        self.like = Like.objects.create(user=self.user, post=self.post)
        self.url = reverse('like-delete-like', kwargs={'post_pk': self.post.pk})

    def test_delete_like_success(self):
        """Тест успешного удаления лайка"""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Like.objects.count(), 0)
        self.assertIn('detail', response.data)

    def test_delete_like_unauthenticated(self):
        """Тест удаления лайка неавторизованным пользователем"""
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Like.objects.count(), 1)

    def test_delete_nonexistent_like(self):
        """Тест удаления несуществующего лайка"""
        self.client.force_authenticate(user=self.user)
        self.like.delete()
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('detail', response.data)
