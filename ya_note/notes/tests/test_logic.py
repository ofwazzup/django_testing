from http import HTTPStatus

from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from .test_utils import (
    BaseNoteTestCase,
    URL_ADD_NOTE,
    URL_LOGIN,
    URL_SUCCESS_PAGE,
    get_edit_url,
    get_delete_url,
    SLUG,
)


class NoteManagementTestCase(BaseNoteTestCase):
    """Тесты для проверки операций с заметками."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.note = None
        cls.existing_note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug=SLUG,
            author=cls.author_user,
        )
        cls.new_note_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug',
        }
        cls.initial_note_count = Note.objects.count()

    def test_create_note_authenticated_user(self):
        """Авторизованный пользователь может создавать заметки."""
        response = self.author_client.post(
            URL_ADD_NOTE, data=self.new_note_data
        )
        self.assertRedirects(response, URL_SUCCESS_PAGE)
        self.assertEqual(
            Note.objects.count(), self.initial_note_count + 1
        )
        created_note = Note.objects.latest('id')
        self.assertEqual(created_note.title, self.new_note_data['title'])
        self.assertEqual(created_note.text, self.new_note_data['text'])
        self.assertEqual(created_note.slug, self.new_note_data['slug'])
        self.assertEqual(created_note.author, self.author_user)

    def test_create_note_anonymous_user(self):
        """Анонимный пользователь не может создавать заметки."""
        response = self.client.post(
            URL_ADD_NOTE, data=self.new_note_data
        )
        expected_redirect_url = f'{URL_LOGIN}?next={URL_ADD_NOTE}'
        self.assertRedirects(response, expected_redirect_url)
        self.assertEqual(Note.objects.count(), self.initial_note_count)

    def test_create_note_duplicate_slug(self):
        """Нельзя создать заметку с дублирующимся slug."""
        self.new_note_data['slug'] = self.existing_note.slug
        response = self.author_client.post(
            URL_ADD_NOTE, data=self.new_note_data
        )
        self.assertFormError(
            response,
            'form',
            'slug',
            errors=(self.existing_note.slug + WARNING),
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
        expected_slug = slugify(self.new_note_data['title'])
        self.assertEqual(created_note.slug, expected_slug)

    def test_edit_note_by_author(self):
        """Автор может редактировать свои заметки."""
        response = self.author_client.post(
            get_edit_url(self.existing_note.slug), data=self.new_note_data
        )
        self.assertRedirects(response, URL_SUCCESS_PAGE)
        self.assertEqual(Note.objects.count(), self.initial_note_count)
        updated_note = Note.objects.get(id=self.existing_note.id)
        self.assertEqual(updated_note.title, self.new_note_data['title'])
        self.assertEqual(updated_note.text, self.new_note_data['text'])
        self.assertEqual(updated_note.slug, self.new_note_data['slug'])

    def test_edit_note_by_other_user(self):
        """Чужой пользователь не может редактировать заметки автора."""
        response = self.reader_client.post(
            get_edit_url(self.existing_note.slug), data=self.new_note_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        unchanged_note = Note.objects.get(id=self.existing_note.id)
        self.assertEqual(unchanged_note.title, self.existing_note.title)
        self.assertEqual(unchanged_note.text, self.existing_note.text)
        self.assertEqual(unchanged_note.slug, self.existing_note.slug)

    def test_delete_note_by_author(self):
        """Автор может удалять свои заметки."""
        response = self.author_client.post(
            get_delete_url(self.existing_note.slug)
        )
        self.assertRedirects(response, URL_SUCCESS_PAGE)
        self.assertEqual(Note.objects.count(), self.initial_note_count - 1)

    def test_delete_note_by_other_user(self):
        """Чужой пользователь не может удалять заметки автора."""
        response = self.reader_client.post(
            get_delete_url(self.existing_note.slug)
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), self.initial_note_count)
