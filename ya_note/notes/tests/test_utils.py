from django.contrib.auth.models import User
from django.test import Client
from notes.models import Note
from django.urls import reverse

URL_ADD_NOTE = reverse('notes:add')
URL_LOGIN = reverse('users:login')
URL_SUCCESS_PAGE = reverse('notes:success')
SLUG = 'note-slug'
URL_NOTES_LIST = reverse('notes:list') 

# Функция для получения URL редактирования заметки
def get_edit_url(slug):
    return reverse('notes:edit', args=(slug,))


# Базовый класс для тестирования заметок
class BaseNoteTestCase:
    """Базовый класс для тестирования заметок."""

    @classmethod
    def setUpTestData(cls):
        """Инициализация тестовых данных."""
        cls.author = User.objects.create(
            username='Автор'
        )
        cls.reader = User.objects.create(
            username='Читатель'
        )
        cls.author_client = Client()
        cls.reader_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug=SLUG,
            author=cls.author,
        )
