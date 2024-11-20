from django.test import Client
from django.contrib.auth.models import User
from notes.models import Note


class TestDataMixin:
    """Миксин для инициализации тестовых данных."""

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
