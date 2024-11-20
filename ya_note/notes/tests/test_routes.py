from http import HTTPStatus
from django.urls import reverse
from .test_utils import BaseNoteTestCase
from django.contrib.auth import get_user_model

# Константы для URL
URL_HOME = reverse('notes:home')
URL_LOGIN = reverse('users:login')
URL_LOGOUT = reverse('users:logout')
URL_SIGNUP = reverse('users:signup')
URL_NOTES_LIST = reverse('notes:list')
URL_NOTES_ADD = reverse('notes:add')
URL_NOTES_SUCCESS = reverse('notes:success')
URL_NOTE_DETAIL = reverse(
    'notes:detail', args=('sample-slug',)
)
URL_NOTE_EDIT = reverse(
    'notes:edit', args=('sample-slug',)
)
URL_NOTE_DELETE = reverse(
    'notes:delete', args=('sample-slug',)
)


class RoutesTests(BaseNoteTestCase):
    """Тесты для проверки маршрутов."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user = get_user_model().objects.create_user(
            username='testuser', password='password'
        )

    def test_public_and_authenticated_accessibility(self):
        """Проверка кодов возврата для пуб и аут пользователей."""
        public_urls = [
            URL_HOME, URL_LOGIN, URL_LOGOUT, URL_SIGNUP
        ]
        authenticated_urls = [
            URL_NOTES_LIST, URL_NOTES_ADD, URL_NOTES_SUCCESS
        ]

        # Проверка пуб страниц и страниц для аут пользователей
        for url in public_urls + authenticated_urls:
            with self.subTest(url=url):
                # Если URL для публичных страниц
                if url in public_urls:
                    client = self.client
                else:
                    # Логиним клиента перед запросом
                    self.client.login(
                        username='testuser', password='password'
                    )
                    client = self.client

                response = client.get(url)
                self.assertEqual(
                    response.status_code, HTTPStatus.OK
                )

    def test_protected_pages_redirect_and_authorization(self):
        """Проверка редиректов и доступа к защищенным страницам."""
        protected_urls = [
            URL_NOTE_DETAIL, URL_NOTE_EDIT, URL_NOTE_DELETE,
            URL_NOTES_ADD, URL_NOTES_SUCCESS, URL_NOTES_LIST,
        ]

        # Проверка редиректов для анонимного пользователя
        for url in protected_urls:
            with self.subTest(url=url):
                redirect_url = f'{URL_LOGIN}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
