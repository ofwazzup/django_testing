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
    admin_client.post(url_news_detail, data=form_data)

    comments_count = Comment.objects.count()

    # Проверка, что коммент был добавлен
    assert comments_count == comments_before + 1

    new_comment = Comment.objects.get(id=Comment.objects.latest('id').id)

    # Проверка текста нового комментария
    assert new_comment.text == form_data['text']

    # Проверка, что автор тот, кто создал
    assert new_comment.author == admin_client.user

    # Проверка, что коммент связан с нужной новостью
    assert new_comment.news is not None


def test_user_cant_use_bad_words(url_news_detail, admin_client):
    """Проверка отправки запрещенных слов."""
    comments_before = comments_before_request()
    bad_words_data = {
        'text': f'Текст, {choice(BAD_WORDS)}, еще текст'
    }

    response = admin_client.post(url_news_detail, data=bad_words_data)

    # Проверка, что форма вернула ошибку
    assertFormError(response, form='form', field='text', errors=WARNING)

    comments_count = Comment.objects.count()

    # Проверка, что кол-во коммент не изменилось
    assert comments_count == comments_before


def test_author_can_delete_comment(
    url_comment_delete, comment, author_client
):
    """Проверка, что автор комментария может его удалить."""
    comment_id = comment.id
    author_client.delete(url_comment_delete)

    # Проверка, что комментарий был удален
    assert not Comment.objects.filter(id=comment_id).exists()


def test_user_cant_delete_comment_of_another_user(
    url_comment_delete, admin_client, comment
):
    """Проверка, что пользователь не может удалить чужой комментарий."""
    response = admin_client.delete(url_comment_delete)

    # Проверка, что возвращается ошибка 404, т.к это чужой комментарий
    assert response.status_code == HTTPStatus.NOT_FOUND

    # Проверка, что комментарий не был удален
    comment.refresh_from_db()
    assert comment.text == COMMENT_TEXT
    assert comment.author is not None
    assert comment.created is not None


def test_author_can_edit_comment(url_comment_edit, comment, author_client):
    """Проверка, что автор комментария может его редактировать."""
    author_client.post(url_comment_edit, data=form_data)

    comment.refresh_from_db()

    # Проверка, что коммент был обновлен
    assert comment.text == NEW_COMMENT_TEXT
    assert comment.author is not None
    assert comment.created is not None


def test_user_cant_edit_comment_of_another_user(
    url_comment_edit, comment, admin_client
):
    """Проверка, что пользователь не может редактировать чужой комментарий."""
    response = admin_client.post(url_comment_edit, data=form_data)

    # Проверка, что возвращается ошибка 404, т.к это чужой комментарий
    assert response.status_code == HTTPStatus.NOT_FOUND

    # Проверка, что комментарий не был изменен
    comment.refresh_from_db()
    assert comment.text == COMMENT_TEXT
    assert comment.author is not None
    assert comment.created is not None
