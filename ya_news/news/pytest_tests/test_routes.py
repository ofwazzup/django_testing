from http import HTTPStatus
import pytest
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'url',
    (
        pytest.lazy_fixture('url_news_home'),  # Главная страница
        pytest.lazy_fixture('url_user_login'),  # Страница входа
        pytest.lazy_fixture('url_user_logout'),  # Страница выхода
        pytest.lazy_fixture('url_user_signup'),  # Страница регистрации
    )
)
@pytest.mark.django_db
def test_pages_availability_for_anonymous_user(client, url):
    """Проверяет доступность страниц для анонима."""
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_detail_page_availability(url_news_detail, client):
    """Проверяет доступность страницы новости для анонима."""
    response = client.get(url_news_detail)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
    ),
)
@pytest.mark.parametrize(
    'url',
    (
        pytest.lazy_fixture('url_comment_edit'),  # Редактирование комментария
        pytest.lazy_fixture('url_comment_delete'),  # Удаление комментария
    ),
)
def test_pages_availability_for_different_users(parametrized_client, url, expected_status):
    """Проверяет доступность страниц для разных пользователей."""
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url',
    (
        pytest.lazy_fixture('url_comment_edit'),  # Редактирование комментария
        pytest.lazy_fixture('url_comment_delete'),  # Удаление комментария
    ),
)
@pytest.mark.django_db
def test_redirects_for_anonymous_user(url, url_user_login, client):
    """Проверяет редирект для анонимного пользователя."""
    expected_url = f'{url_user_login}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
