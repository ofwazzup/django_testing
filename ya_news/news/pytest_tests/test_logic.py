from http import HTTPStatus
from random import choice

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment
from news.pytest_tests.conftest import COMMENT_TEXT

pytestmark = pytest.mark.django_db

NEW_COMMENT_TEXT = 'Новый текст комментария'
form_data = {'text': NEW_COMMENT_TEXT}


def comments_before_request():
    """Возвращает количество комментариев перед выполнением запроса."""
    return Comment.objects.count()


def test_anonymous_user_cant_create_comment(url_news_detail, client):
    """Проверка, что анонимный пользователь не может создать комментарий."""
    comments_before = comments_before_request()
    client.post(url_news_detail, data=form_data)
    comments_count = Comment.objects.count()

    # Проверка, что кол-во коммент не изменилось
    assert comments_count == comments_before


def test_user_can_create_comment(url_news_detail, admin_client):
    """Проверка, что авторизованный пользователь может создать комментарий."""
    comments_before = comments_before_request()
    response = admin_client.post(url_news_detail, data=form_data)

    # Проверка редиректа на раздел комментариев
    assertRedirects(response, f'{url_news_detail}#comments')

    comments_count = Comment.objects.count()
    # Проверка, что коммент был добавлен
    assert comments_count == comments_before + 1

    new_comment = Comment.objects.latest('id')
    # Проверка текста нового комментария
    assert new_comment.text == form_data['text']
    assert new_comment.author is not None


def test_user_cant_use_bad_words(url_news_detail, admin_client):
    """Проверка отправки запрещенных слов."""
    comments_before = comments_before_request()
    bad_words_data = {'text': f'Текст, {choice(BAD_WORDS)}, еще текст'}

    response = admin_client.post(url_news_detail, data=bad_words_data)
    # Проверка, что форма вернула ошибку
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )

    comments_count = Comment.objects.count()
    # Проверка, что кол-во коммент не изменилось
    assert comments_count == comments_before


def test_author_can_delete_comment(url_comment_delete, url_news_detail, author_client):
    """Проверка, что автор комментария может его удалить."""
    comments_before = comments_before_request()
    response = author_client.delete(url_comment_delete)

    # Проверка редиректа на раздел комментариев после удаления
    assertRedirects(response, f'{url_news_detail}#comments')

    comments_count = Comment.objects.count()
    # Проверка, что коммент был удален
    assert comments_count == comments_before - 1


def test_user_cant_delete_comment_of_another_user(url_comment_delete, admin_client):
    """Проверка, что пользователь не может удалить чужой комментарий."""
    comments_before = comments_before_request()
    response = admin_client.delete(url_comment_delete)

    # Проверка, что возвращается ошибка 404,т.к это чужой комментарий
    assert response.status_code == HTTPStatus.NOT_FOUND

    comments_count = Comment.objects.count()
    # Проверка, что количество комментариев не изменилось
    assert comments_count == comments_before


def test_author_can_edit_comment(url_comment_edit, url_news_detail, comment, author_client):
    """Проверка, что автор комментария может его редактировать."""
    response = author_client.post(url_comment_edit, data=form_data)

    # Проверка редиректа на раздел комментариев после редактирования
    assertRedirects(response, f'{url_news_detail}#comments')

    comment.refresh_from_db()
    # Проверка, что коммент был обновлен
    assert comment.text == NEW_COMMENT_TEXT
    assert comment.author is not None
    assert comment.created is not None


def test_user_cant_edit_comment_of_another_user(url_comment_edit, comment, admin_client):
    """Проверка, что пользователь не может редактировать чужой комментарий."""
    response = admin_client.post(url_comment_edit, data=form_data)

    # Проверка, что возвращается ошибка 404,т.к это чужой комментарий
    assert response.status_code == HTTPStatus.NOT_FOUND

    comment.refresh_from_db()
    # Проверка, что коммент не был изменен
    assert comment.text == COMMENT_TEXT
    assert comment.author is not None
    assert comment.created is not None
