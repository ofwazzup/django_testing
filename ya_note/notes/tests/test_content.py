from django.test import TestCase
from django.urls import reverse
from test_setup import TestDataMixin
from notes.forms import NoteForm


# Функция для получения URL редактирования заметки
def get_edit_url(slug):
    return reverse('notes:edit', args=(slug,))


URL_NOTES_LIST = reverse('notes:list')
URL_ADD_NOTE = reverse('notes:add')
URL_EDIT_NOTE = get_edit_url


class NoteContentTestCase(TestDataMixin, TestCase):
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
            URL_EDIT_NOTE(self.note.slug): NoteForm,
        }

        for url, form_class in urls_to_check.items():
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(
                    response.context['form'],
                    form_class,
                    msg=f"На странице {url} ожидалась форма типа {form_class}."
                )
