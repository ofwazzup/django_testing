from django.test import Client, TestCase
from django.urls import reverse
from notes.models import Note
from notes.tests.test_routes import User


class NoteContentTestCase(TestCase):
    """Тесты для проверки контента и форм на страницах приложения."""

    @classmethod
    def setUpTestData(cls):
        """Инициализация тестовых данных."""

        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.author_client = Client()
        cls.reader_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug',
            author=cls.author,
        )
        cls.url_notes_list = reverse('notes:list')
        cls.url_add_note = reverse('notes:add')
        cls.url_edit_note = reverse('notes:edit', args=(cls.note.slug,))

    def test_notes_list_visibility_for_users(self):
        """
        Проверяет, что:
        1. Автор видит свои заметки в списке.
        2. Чужие заметки не отображаются в списке другого пользователя.
        """

        user_access_cases = (
            (self.author_client, True),  # Автор видит свою заметку
            (self.reader_client, False),  # Читатель не видит чужую заметку
        )
        for client, should_see in user_access_cases:
            with self.subTest(client=client):
                response = client.get(self.url_notes_list)
                object_list = response.context['object_list']
                self.assertEqual(self.note in object_list, should_see)

    def test_pages_contain_form(self):
        """Проверяет, что страницы содержат форму."""

        urls_to_check = (self.url_add_note, self.url_edit_note)
        for url in urls_to_check:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
