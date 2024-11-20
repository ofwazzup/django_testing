from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'url_fixture, client_fixture, expected_status',
    (
        (pytest.lazy_fixture('url_news_home'), 'client', HTTPStatus.OK),
        (pytest.lazy_fixture('url_user_login'), 'client', HTTPStatus.OK),
        (pytest.lazy_fixture('url_user_logout'), 'client', HTTPStatus.OK),
        (pytest.lazy_fixture('url_user_signup'), 'client', HTTPStatus.OK),
        (pytest.lazy_fixture('url_news_detail'), 'client', HTTPStatus.OK),
        (
            pytest.lazy_fixture('url_comment_edit'),
            'author_client', HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('url_comment_delete'),
            'author_client', HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('url_comment_edit'),
            'admin_client', HTTPStatus.NOT_FOUND
        ),
        (
            pytest.lazy_fixture('url_comment_delete'),
            'admin_client', HTTPStatus.NOT_FOUND
        ),
    )
)
def test_page_status_codes(
    url_fixture, client_fixture, expected_status, request
):
    """Проверяет код ответа для различных страниц и пользователей."""
    url = request.getfixturevalue(url_fixture)
    client = request.getfixturevalue(client_fixture)
    response = client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url_fixture, login_url_fixture',
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
def test_redirects_for_anonymous_user(
    url_fixture, login_url_fixture, client, request
):
    """Проверяет редирект для анонимного пользователя."""
    url = request.getfixturevalue(url_fixture)
    login_url = request.getfixturevalue(login_url_fixture)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
