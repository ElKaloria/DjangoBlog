from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from blog.models import Post, CustomUser



class PostListAPITestCase(APITestCase):
    """Тесты для получения списка постов"""

    def setUp(self):
        self.user1 = CustomUser.objects.create_user(
            username='user1', email='user1@example.com', password='Pass123!'
        )
        self.user2 = CustomUser.objects.create_user(
            username='user2', email='user2@example.com', password='Pass123!'
        )
        self.post1 = Post.objects.create(
            title='Post 1',
            content='Content 1',
            author=self.user1
        )
        self.post2 = Post.objects.create(
            title='Post 2',
            content='Content 2',
            author=self.user2
        )
        self.url = reverse('post-list')

    def test_list_posts_unauthenticated(self):
        """Тест фильтрации постов по автору"""
        response = self.client.get(self.url, {'author': 'user1'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['author'], 'user1')

    def test_list_posts_ordering(self):
        """Тест сортировки постов"""
        response = self.client.get(self.url, {'ordering': 'author'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['author'], 'user1')

        response = self.client.get(self.url, {'ordering': '-author'})
        self.assertEqual(response.data['results'][0]['author'], 'user2')


class PostCreateAPITestCase(APITestCase):
    """Тесты для создания постов"""

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser', email='test@example.com', password='Pass123!'
        )
        self.url = reverse('post-list')

    def test_create_post_authenticated(self):
        """Тест создания поста авторизованным пользователем"""
        self.client.force_authenticate(user=self.user)
        data = {'title': 'New Post', 'content': 'Post content'}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(response.data['title'], 'New Post')
        self.assertEqual(response.data['author'], 'testuser')

    def test_create_post_unauthenticated(self):
        """Тест создания поста неавторизованным пользователем"""
        data = {'title': 'New Post', 'content': 'Post content'}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_post_missing_fields(self):
        """Тест создания поста без обязательных полей"""
        self.client.force_authenticate(user=self.user)
        data = {'title': 'New Post'}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PostDetailAPITestCase(APITestCase):
    """Тесты для работы с отдельным постом"""

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
        self.url = reverse('post-detail', kwargs={'pk': self.post.pk})

    def test_retrieve_post(self):
        """Тест получения поста"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Post')
        self.assertIn('amount_of_likes', response.data)
        self.assertIn('amount_of_comments', response.data)

    def test_retrieve_post_not_found(self):
        """Тест получения несуществующего поста"""
        url = reverse('post-detail', kwargs={'pk': 9999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class PostUpdateAPITestCase(APITestCase):
    """Тесты для обновления постов"""

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
        self.url = reverse('post-detail', kwargs={'pk': self.post.pk})

    def test_update_post_as_author(self):
        """Тест обновления поста автором"""
        self.client.force_authenticate(user=self.user)
        data = {'title': 'Updated Title', 'content': 'Updated content'}
        response = self.client.put(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Updated Title')

    def test_update_post_as_other_user(self):
        """Тест обновления поста другим пользователем"""
        self.client.force_authenticate(user=self.other_user)
        data = {'title': 'Hacked Title', 'content': 'Hacked content'}
        response = self.client.put(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_partial_update_post(self):
        """Тест частичного обновления поста"""
        self.client.force_authenticate(user=self.user)
        data = {'title': 'Partial Update'}
        response = self.client.patch(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Partial Update')
        self.assertEqual(self.post.content, 'Test content')  # Не изменилось


class PostDeleteAPITestCase(APITestCase):
    """Тесты для удаления постов"""

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
        self.url = reverse('post-detail', kwargs={'pk': self.post.pk})

    def test_delete_post_as_author(self):
        """Тест удаления поста автором"""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('detail', response.data)
        self.assertEqual(Post.objects.count(), 0)

    def test_delete_post_as_other_user(self):
        """Тест удаления поста другим пользователем"""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Post.objects.count(), 1)

    def test_delete_post_unauthenticated(self):
        """Тест удаления поста неавторизованным пользователем"""
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Post.objects.count(), 1)