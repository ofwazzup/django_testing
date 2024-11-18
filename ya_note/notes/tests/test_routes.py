from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from notes.models import Note

User = get_user_model()


class RoutesTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Создание тестовых пользователей и тестовой заметки
        cls.author_user = User.objects.create(username='Author')
        cls.reader_user = User.objects.create(username='Reader')
        cls.author_client = Client()
        cls.reader_client = Client()
        cls.author_client.force_login(cls.author_user)
        cls.reader_client.force_login(cls.reader_user)
        cls.note = Note.objects.create(
            title='Sample Title',
            text='Sample Text',
            slug='sample-slug',
            author=cls.author_user,
        )
        # Определение URL-адресов
        cls.url_home = reverse('notes:home')
        cls.url_login = reverse('users:login')
        cls.url_logout = reverse('users:logout')
        cls.url_signup = reverse('users:signup')
        cls.url_notes_list = reverse('notes:list')
        cls.url_notes_add = reverse('notes:add')
        cls.url_notes_success = reverse('notes:success')
        cls.url_note_detail = reverse('notes:detail', args=(cls.note.slug,))
        cls.url_note_edit = reverse('notes:edit', args=(cls.note.slug,))
        cls.url_note_delete = reverse('notes:delete', args=(cls.note.slug,))

    def test_public_pages_accessibility(self):
        """Проверяет доступность страниц для всех пользователей."""
        public_urls = (
            self.url_home,
            self.url_login,
            self.url_logout,
            self.url_signup,
        )
        for url in public_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_authenticated_user_pages(self):
        """Проверяет доступность страниц для аутентифицированного пользователя."""
        authenticated_urls = (
            self.url_notes_list,
            self.url_notes_add,
            self.url_notes_success,
        )
        for url in authenticated_urls:
            with self.subTest(url=url):
                response = self.reader_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_note_pages_authorization(self):
        """Проверяет доступ к страницам заметки."""
        user_status_pairs = (
            (self.author_client, HTTPStatus.OK),
            (self.reader_client, HTTPStatus.NOT_FOUND),
        )
        restricted_urls = (
            self.url_note_detail,
            self.url_note_edit,
            self.url_note_delete,
        )
        for client, expected_status in user_status_pairs:
            for url in restricted_urls:
                with self.subTest(url=url, client=client):
                    response = client.get(url)
                    self.assertEqual(response.status_code, expected_status)

    def test_anonymous_user_redirects(self):
        """Проверяет редиректы для неавторизованных пользователей."""
        protected_urls = (
            self.url_note_detail,
            self.url_note_edit,
            self.url_note_delete,
            self.url_notes_add,
            self.url_notes_success,
            self.url_notes_list,
        )
        for url in protected_urls:
            with self.subTest(url=url):
                redirect_url = f'{self.url_login}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
