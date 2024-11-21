from django.contrib.auth.models import User
from django.test import Client
from notes.models import Note
from django.urls import reverse

# Константы для URL
URL_ADD_NOTE = reverse('notes:add')
URL_LOGIN = reverse('users:login')
URL_SUCCESS_PAGE = reverse('notes:success')
URL_NOTES_LIST = reverse('notes:list')
URL_HOME = reverse('notes:home')
URL_LOGOUT = reverse('users:logout')
URL_SIGNUP = reverse('users:signup')
URL_NOTE_DETAIL = reverse(
    'notes:detail', args=('sample-slug',)
)
URL_NOTE_EDIT = reverse(
    'notes:edit', args=('sample-slug',)
)
URL_NOTE_DELETE = reverse(
    'notes:delete', args=('sample-slug',)
)
SLUG = 'note-slug'


def get_delete_url(slug):
    return reverse('notes:delete', args=[slug])


def get_edit_url(slug):
    return reverse('notes:edit', args=(slug,))


# Базовый класс для тестирования
class BaseNoteTestCase:
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
