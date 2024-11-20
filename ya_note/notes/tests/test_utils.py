from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from notes.models import Note

# Константы с урлами
URL_NOTES_LIST = reverse('notes:list')
URL_ADD_NOTE = reverse('notes:add')


# Функция для получения URL редактирования заметки
def get_edit_url(slug):
    return reverse('notes:edit', args=(slug,))


class BaseNoteTestCase(TestCase):
    """Базовый класс для тестирования заметок."""

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
