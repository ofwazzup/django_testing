from django.test import Client, TestCase

from test_utils import (
    BaseNoteTestCase,
    URL_NOTES_LIST,
    URL_ADD_NOTE,
    get_edit_url
)

from notes.forms import NoteForm
from notes.models import Note


class NoteContentTestCase(BaseNoteTestCase):
    """Тесты для проверки контента и форм на страницах приложения."""

    def test_notes_list_visibility_for_users(self):
        """
        Проверяет, что:
        1. Автор видит свои заметки в списке.
        2. Чужие заметки не отображаются в списке другого пользователя.
        """
        user_access_cases = (
            (self.author_client, True),
            (self.reader_client, False),
        )

        for client, should_see in user_access_cases:
            with self.subTest(client=client):
                response = client.get(URL_NOTES_LIST)
                object_list = response.context['object_list']
                self.assertEqual(self.note in object_list, should_see)

    def test_pages_contain_form(self):
        """Проверяет, что страницы содержат форму правильного типа."""
        urls_to_check = {
            URL_ADD_NOTE: NoteForm,
            get_edit_url(self.note.slug): NoteForm,
        }

        for url, form_class in urls_to_check.items():
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                form = response.context['form']
                self.assertIsInstance(
                    form,
                    form_class,
                    msg=f"На странице {url} ожидалась форма типа {form_class}."
                )
