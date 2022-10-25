import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post, User

# Создаем временную папку для медиа-файлов;
# на момент теста медиа папка будет переопределена
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username="NoNoName")  # Создаем пользователя
        cls.form = PostCreateFormTests()  # Создаем форму, если нужна проверка атрибутов
        # Создаем запись в базе данных для проверки сушествующего slug
        cls.group = Group.objects.create(
            title="Тестовый заголовок группы",
            slug="test-slug",
            description="Тестовое описание",
        )
        # Создадим запись в БД
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый пост",
            group=cls.group,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Модуль shutil - библиотека Python с удобными инструментами
        # для управления файлами и директориями:
        # создание, удаление, копирование, перемещение, изменение папок и файлов
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()  # Создаем неавторизованный клиент
        self.authorized_client = Client()  # Создаем авторизированного клиента
        self.authorized_client.force_login(self.user)  # Авторизуем пользователя

    def test_create_post(self):
        """Проверка, что валидная форма создаёт пост"""
        posts_count = Post.objects.count()
        form_data = {"text": "Текст записанный в форму", "group": self.group.id}
        response = self.authorized_client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(
            Post.objects.filter(
                text="Текст записанный в форму", group=self.group.id, author=self.user
            ).exists()
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_post_edit(self):
        """Проверка, что валидная форма редактирует пост"""
        self.post = Post.objects.create(
            text="Тестовый текст", author=self.user, group=self.group
        )
        old_text = self.post
        self.group2 = Group.objects.create(
            title="Тестовая группа2", slug="test-group", description="Описание"
        )
        form_data = {"text": "Текст записанный в форму", "group": self.group2.id}
        response = self.authorized_client.post(
            reverse("posts:post_edit", args=(self.post.id,)),
            data=form_data,
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(
            Post.objects.filter(
                group=self.group2.id, author=self.user, pub_date=self.post.pub_date
            ).exists()
        )
        error_name1 = "Пользователь не может изменить содержание поста"
        self.assertNotEqual(old_text.text, form_data["text"], error_name1)
        error_name2 = "Пользователь не может изменить группу поста"
        self.assertNotEqual(old_text.group, form_data["group"], error_name2)
