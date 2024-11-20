from http import HTTPStatus
from django.test import TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

from .test_utils import (
    BaseNoteTestCase,
    URL_ADD_NOTE,
    URL_LOGIN,
    URL_SUCCESS_PAGE,
    SLUG,
    get_edit_url
)


class NoteManagementTestCase(BaseNoteTestCase, TestCase):
    """Тесты для проверки операций с заметками."""

    @classmethod
    def setUpTestData(cls):
        """Инициализация тестовых данных."""
        super().setUpTestData()
        cls.existing_note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug=SLUG,
            author=cls.author,
        )
        cls.new_note_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug',  # slug задается вручную
        }
        cls.initial_note_count = Note.objects.count()
        cls.url_edit_note = get_edit_url(cls.existing_note.slug)
        cls.url_delete_note = reverse(
            'notes:delete', args=(cls.existing_note.slug,)
        )

    def test_create_note_authenticated_user(self):
        """Авторизованный пользователь может создавать заметки."""
        response = self.author_client.post(
            URL_ADD_NOTE, data=self.new_note_data
        )
        self.assertRedirects(response, URL_SUCCESS_PAGE)
        self.assertEqual(Note.objects.count(), self.initial_note_count + 1)
        created_note = Note.objects.latest('id')
        self.assertEqual(created_note.title, self.new_note_data['title'])
        self.assertEqual(created_note.text, self.new_note_data['text'])
        self.assertEqual(created_note.slug, self.new_note_data['slug'])
        self.assertEqual(created_note.author, self.author)

    def test_create_note_anonymous_user(self):
        """Анонимный пользователь не может создавать заметки."""
        response = self.client.post(URL_ADD_NOTE, data=self.new_note_data)
        expected_redirect_url = f'{URL_LOGIN}?next={URL_ADD_NOTE}'
        self.assertRedirects(response, expected_redirect_url)
        self.assertEqual(Note.objects.count(), self.initial_note_count)

    def test_create_note_duplicate_slug(self):
        """Нельзя создать заметку с дублирующимся slug."""
        self.new_note_data['slug'] = SLUG
        response = self.author_client.post(
            URL_ADD_NOTE, data=self.new_note_data
        )
        # Убедимся, что форма вернет ошибку, если slug уже существует
        self.assertFormError(
            response,
            'form',
            'slug',
            errors=(SLUG + WARNING),
        )
        self.assertEqual(Note.objects.count(), self.initial_note_count)

    def test_create_note_empty_slug(self):
        """Если slug не указан, он генерируется автоматически."""
        self.new_note_data.pop('slug')
        response = self.author_client.post(
            URL_ADD_NOTE, data=self.new_note_data
        )
        self.assertRedirects(response, URL_SUCCESS_PAGE)
        self.assertEqual(Note.objects.count(), self.initial_note_count + 1)
        created_note = Note.objects.latest('id')

        # Генерация slug на основе title
        expected_slug = slugify(self.new_note_data['title'])

        # Убедимся, что slug сгенерирован правильно
        self.assertEqual(created_note.slug, expected_slug)

    def test_edit_note_by_author(self):
        """Автор может редактировать свои заметки."""
        response = self.author_client.post(
            self.url_edit_note,
            data=self.new_note_data
        )
        self.assertRedirects(response, self.url_edit_note)
        edited_note = Note.objects.get(id=self.existing_note.id)
        self.assertEqual(edited_note.title, self.new_note_data['title'])
        self.assertEqual(edited_note.text, self.new_note_data['text'])
        self.assertEqual(edited_note.slug, self.new_note_data['slug'])

    def test_delete_note_by_author(self):
        """Автор может удалить свои заметки."""
        response = self.author_client.post(self.url_delete_note)
        self.assertRedirects(response, URL_SUCCESS_PAGE)
        self.assertEqual(Note.objects.count(), self.initial_note_count - 1)

    def test_delete_note_by_other_user(self):
        """Пользователь не может удалить чужие заметки."""
        self.new_note_data['slug'] = 'another-slug'
        another_note = Note.objects.create(
            title='Заголовок для удаления',
            text='Текст заметки',
            slug='another-slug',
            author=self.other_user,
        )
        url_delete_note = reverse('notes:delete', args=(another_note.slug,))
        response = self.author_client.post(url_delete_note)
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertEqual(Note.objects.count(), self.initial_note_count)

    def test_edit_note_by_other_user(self):
        """Пользователь не может редактировать чужие заметки."""
        self.new_note_data['slug'] = 'edit-by-other'
        another_note = Note.objects.create(
            title='Заголовок для редактирования',
            text='Текст заметки',
            slug='edit-by-other',
            author=self.other_user,
        )
        url_edit_note = get_edit_url(another_note.slug)
        response = self.author_client.post(
            url_edit_note, data=self.new_note_data
        )
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertEqual(another_note.title, 'Заголовок для редактирования')
