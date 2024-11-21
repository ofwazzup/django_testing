from http import HTTPStatus
from random import choice
import pytest

from pytest_django.asserts import assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

from news.pytest_tests.conftest import COMMENT_TEXT

pytestmark = pytest.mark.django_db

NEW_COMMENT_TEXT = 'Новый текст комментария'
form_data = {'text': NEW_COMMENT_TEXT}


def test_anonymous_user_cant_create_comment(url_news_detail, client):
    """Анонимный пользователь не может создать комментарий."""
    initial_count = Comment.objects.count()
    client.post(url_news_detail, data=form_data)
    assert Comment.objects.count() == initial_count


def test_user_can_create_comment(url_news_detail, admin_client, admin_user):
    """Авторизованный пользователь может создать комментарий."""
    Comment.objects.all().delete()
    response = admin_client.post(url_news_detail, data=form_data)

    # Проверяем, что комментарий был создан
    assert response.status_code == HTTPStatus.OK
    assert Comment.objects.count() == 1

    new_comment = Comment.objects.first()
    assert new_comment.text == NEW_COMMENT_TEXT
    assert new_comment.author == admin_user
    assert new_comment.news is not None


def test_user_cant_use_bad_words(url_news_detail, admin_client):
    """Пользователь не может использовать запрещенные слова."""
    initial_count = Comment.objects.count()
    bad_words_data = {'text': f'Текст, {choice(BAD_WORDS)}, еще текст'}

    response = admin_client.post(url_news_detail, data=bad_words_data)

    # Проверяем, что вернулась ошибка формы с предупреждением
    assertFormError(response, form='form', field='text', errors=WARNING)
    assert Comment.objects.count() == initial_count


def test_author_can_delete_comment(url_comment_delete, comment, author_client):
    """Автор комментария может удалить свой комментарий."""
    response = author_client.delete(url_comment_delete)
    assert response.status_code == HTTPStatus.NO_CONTENT
    assert not Comment.objects.filter(id=comment.id).exists()


def test_user_cant_delete_comment_of_another_user(url_comment_delete, admin_client, comment):
    """Пользователь не может удалить чужой комментарий."""
    response = admin_client.delete(url_comment_delete)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == COMMENT_TEXT


def test_author_can_edit_comment(url_comment_edit, comment, author_client):
    """Автор комментария может его редактировать."""
    response = author_client.post(url_comment_edit, data=form_data)

    assert response.status_code == HTTPStatus.OK
    comment.refresh_from_db()
    assert comment.text == NEW_COMMENT_TEXT
    assert comment.author is not None
    assert comment.created is not None


def test_user_cant_edit_comment_of_another_user(url_comment_edit, comment, admin_client):
    """Пользователь не может редактировать чужой комментарий."""
    response = admin_client.post(url_comment_edit, data=form_data)

    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == COMMENT_TEXT
    assert comment.author is not None
    assert comment.created is not None
