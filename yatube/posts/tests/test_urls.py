from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


class URLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username="NoName")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Тестовое описание",
        )
        # Создадим запись в БД тестовый пост
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый пост",
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            reverse('posts:index'): ['posts/index.html', HTTPStatus.OK],
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
                ['posts/group_list.html', HTTPStatus.OK],
            reverse('posts:profile', kwargs={'username': self.user.username}):
                ['posts/profile.html', HTTPStatus.OK],
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}):
                ['posts/post_detail.html', HTTPStatus.OK],
            reverse('posts:post_create'):
                ['posts/create_post.html', HTTPStatus.FOUND],
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}):
                ['posts/create_post.html', HTTPStatus.FOUND],
        }

        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template[0])

    def test_posts_post_id_edit_url_exists_at_author(self):
        """Страница /posts/post_id/edit/ доступна только автору."""
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(URLTests.user)
        response = self.authorized_client.get(
            f"/posts/{URLTests.post.id}/edit/"
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_url_exists_at_desired_location_authorized(self):
        """Страница /create/ доступна только авторизованному пользователю."""
        response = self.guest_client.get("/create/", follow=True)
        self.assertRedirects(response, "/auth/login/?next=/create/")

    def test_unexisting_page_at_desired_location(self):
        """Страница /unexisting_page/ должна выдать ошибку."""
        response = self.guest_client.get("/unexisting_page/")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_exists_at_desired_location(self):
        """Проверяем общедоступные страницы"""
        templates = [
            "/",
            f"/group/{URLTests.group.slug}/",
            f"/profile/{URLTests.user}/",
            f"/posts/{URLTests.post.id}/",
        ]
        for adress in templates:
            with self.subTest(adress):
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.OK)
