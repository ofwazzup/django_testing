from http import HTTPStatus
from random import choice
import pytest
from news.forms import BAD_WORDS, WARNING
from news.models import Comment
from news.pytest_tests.conftest import COMMENT_TEXT
from pytest_django.asserts import assertFormError, assertRedirects

NEW_COMMENT_TEXT = 'Новый текст комментария'
form_data = {'text': NEW_COMMENT_TEXT}


def comments_before_request():
    """Возвращает количество комментариев перед выполнением запроса."""
    return Comment.objects.count()


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(url_news_detail, client):
    """Проверка, что анонимный пользователь не может создать комментарий."""
    COMMENTS_BEFORE_REQUEST = comments_before_request()
    client.post(url_news_detail, data=form_data)
    comments_count = Comment.objects.count()
    # Убедитесь, что количество комментариев не изменилось
    assert comments_count == COMMENTS_BEFORE_REQUEST


@pytest.mark.django_db
def test_user_can_create_comment(url_news_detail, admin_client):
    """Проверка, что авторизованный пользователь может создать комментарий."""
    COMMENTS_BEFORE_REQUEST = comments_before_request()
    response = admin_client.post(url_news_detail, data=form_data)
    # Проверка редиректа на раздел комментариев
    assertRedirects(response, f'{url_news_detail}#comments')
    comments_count = Comment.objects.count()
    # Убедитесь, что комментарий был добавлен
    assert comments_count == COMMENTS_BEFORE_REQUEST + 1
    new_comment = Comment.objects.get()
    # Проверка текста нового комментария
    assert new_comment.text == form_data['text']


@pytest.mark.django_db
def test_user_cant_use_bad_words(url_news_detail, admin_client):
    """Проверка отправки запрещенных слов."""
    COMMENTS_BEFORE_REQUEST = comments_before_request()
    bad_words_data = {'text': f'Текст, {choice(BAD_WORDS)}, еще текст'}
    response = admin_client.post(url_news_detail, data=bad_words_data)
    # Проверка, что форма вернула ошибку с предупреждением
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    # Убедитесь, что количество комментариев не изменилось
    assert comments_count == COMMENTS_BEFORE_REQUEST


@pytest.mark.django_db
def test_author_can_delete_comment(
    url_comment_delete, url_news_detail, author_client
):
    """Проверка, что автор комментария может его удалить."""
    COMMENTS_BEFORE_REQUEST = comments_before_request()
    response = author_client.delete(url_comment_delete)
    # Проверка редиректа на раздел комментариев после удаления
    assertRedirects(response, f'{url_news_detail}#comments')
    comments_count = Comment.objects.count()
    # Убедитесь, что комментарий был удален
    assert comments_count == COMMENTS_BEFORE_REQUEST - 1


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(
    url_comment_delete, admin_client
):
    """Проверка, что пользователь не может удалить чужой комментарий."""
    COMMENTS_BEFORE_REQUEST = comments_before_request()
    response = admin_client.delete(url_comment_delete)
    # Проверка, что возвращается ошибка 404, так как это чужой комментарий
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    # Убедитесь, что количество комментариев не изменилось
    assert comments_count == COMMENTS_BEFORE_REQUEST


@pytest.mark.django_db
def test_author_can_edit_comment(
    url_comment_edit, url_news_detail, comment, author_client
):
    """Проверка, что автор комментария может его редактировать."""
    response = author_client.post(url_comment_edit, data=form_data)
    # Проверка редиректа на раздел комментариев после редактирования
    assertRedirects(response, f'{url_news_detail}#comments')
    comment.refresh_from_db()
    # Убедитесь, что текст комментария был обновлен
    assert comment.text == NEW_COMMENT_TEXT


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(
    url_comment_edit, comment, admin_client
):
    """Проверка, что пользователь не может редактировать чужой комментарий."""
    response = admin_client.post(url_comment_edit, data=form_data)
    # Проверка, что возвращается ошибка 404, так как это чужой комментарий
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    # Убедитесь, что текст комментария не был изменен
    assert comment.text == COMMENT_TEXT
