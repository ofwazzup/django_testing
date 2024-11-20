from http import HTTPStatus
import pytest
from pytest_django.asserts import assertRedirects

pytestmark = pytest.mark.django_db

# Тест для проверки всех кодов ответов
@pytest.mark.parametrize(
    'url, client, expected_status',
    (
        (pytest.lazy_fixture('url_news_home'), pytest.lazy_fixture('client'), HTTPStatus.OK),
        (pytest.lazy_fixture('url_user_login'), pytest.lazy_fixture('client'), HTTPStatus.OK),
        (pytest.lazy_fixture('url_user_logout'), pytest.lazy_fixture('client'), HTTPStatus.OK),
        (pytest.lazy_fixture('url_user_signup'), pytest.lazy_fixture('client'), HTTPStatus.OK),
        (pytest.lazy_fixture('url_news_detail'), pytest.lazy_fixture('client'), HTTPStatus.OK),
        (
            pytest.lazy_fixture('url_comment_edit'),
            pytest.lazy_fixture('author_client'), HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('url_comment_edit'),
            pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND
        ),
    )
)
def test_pages_availability(url, client, expected_status):
    """Проверяет доступность страниц для разных пользователей и статусы ответов."""
    response = client.get(url)
    assert response.status_code == expected_status

# Тест для проверки редиректов
@pytest.mark.parametrize(
    'url, expected_redirect_url',
    (
        (
            pytest.lazy_fixture('url_comment_edit'),
            pytest.lazy_fixture('url_user_login')
        ),
        (
            pytest.lazy_fixture('url_comment_delete'),
            pytest.lazy_fixture('url_user_login')
        ),
    )
)
def test_redirects_for_anonymous_user(url, expected_redirect_url, client):
    """Проверяет редиректы для анонимного пользователя."""
    expected_url = f'{expected_redirect_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
