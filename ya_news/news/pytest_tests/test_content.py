import pytest
from django.conf import settings

pytestmark = pytest.mark.django_db


def test_news_count(eleven_news, url_news_home, client):
    """Проверка глав страницы вывода не более 10 новостей."""
    response = client.get(url_news_home)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(eleven_news, url_news_home, client):
    """Проверка сортировки от самой свежей к самой старой."""
    response = client.get(url_news_home)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(news_with_ten_comments, url_news_detail, client):
    """Старые комментарии должны быть в начале, новые — в конце."""
    response = client.get(url_news_detail)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()

    created_list = [comment.created for comment in all_comments]
    assert created_list == sorted(created_list), (
        'Комментарии отсортированы неправильно'
    )


def test_anonymous_client_has_no_form(url_news_detail, client):
    """Проверка, что анонимному пользователю недоступна форма комментария."""
    response = client.get(url_news_detail)
    assert 'form' not in response.context


def test_authorized_client_has_form(url_news_detail, author_client):
    """Проверка, что авторизованный пользователь видит форму комментария."""
    response = author_client.get(url_news_detail)
    assert 'form' in response.context
    from news.forms import CommentForm
    assert isinstance(response.context['form'], CommentForm)
