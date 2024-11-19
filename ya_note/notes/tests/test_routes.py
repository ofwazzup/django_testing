from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

URL_HOME = reverse('notes:home')
URL_LOGIN = reverse('users:login')
URL_LOGOUT = reverse('users:logout')
URL_SIGNUP = reverse('users:signup')
URL_NOTES_LIST = reverse('notes:list')
URL_NOTES_ADD = reverse('notes:add')
URL_NOTES_SUCCESS = reverse('notes:success')


class RoutesTests(TestCase):
    """Тесты для проверки маршрутов."""

    @classmethod
    def setUpTestData(cls):
        cls.author_user = get_user_model().objects.create(username='Author')
        cls.reader_user = get_user_model().objects.create(username='Reader')
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

        cls.url_note_detail = reverse('notes:detail', args=(cls.note.slug,))
        cls.url_note_edit = reverse('notes:edit', args=(cls.note.slug,))
        cls.url_note_delete = reverse('notes:delete', args=(cls.note.slug,))

    def test_public_and_authenticated_accessibility(self):
        """
        Проверка кодов возврата
        для публичных и аутентифицированных пользователей.
        """
        public_urls = [URL_HOME, URL_LOGIN, URL_LOGOUT, URL_SIGNUP]
        authenticated_urls = [URL_NOTES_LIST, URL_NOTES_ADD, URL_NOTES_SUCCESS]

        # Проверка публичных страниц
        for url in public_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

        # Проверка страниц для аутентифицированного пользователя
        for url in authenticated_urls:
            with self.subTest(url=url):
                response = self.reader_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_protected_pages_redirect_and_authorization(self):
        """Проверка редиректов и доступа к защищенным страницам."""
        protected_urls = [
            self.url_note_detail,
            self.url_note_edit,
            self.url_note_delete,
            URL_NOTES_ADD,
            URL_NOTES_SUCCESS,
            URL_NOTES_LIST,
        ]

        # Проверка редиректов для анонимного пользователя
        for url in protected_urls:
            with self.subTest(url=url):
                redirect_url = f'{URL_LOGIN}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

        # Проверка доступа для авторизованных пользователей
        restricted_urls = [
            self.url_note_detail, self.url_note_edit, self.url_note_delete
        ]
        user_status_pairs = [
            (self.author_client, HTTPStatus.OK),
            (self.reader_client, HTTPStatus.NOT_FOUND),
        ]

        for client, expected_status in user_status_pairs:
            for url in restricted_urls:
                with self.subTest(client=client, url=url):
                    response = client.get(url)
                    self.assertEqual(response.status_code, expected_status)
