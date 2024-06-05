from http import HTTPStatus
import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture

URL_NEWS_HOME = lazy_fixture('url_news_home')
URL_NEWS_DETAIL = lazy_fixture('url_news_detail')
URL_USERS_SIGNUP = lazy_fixture('url_users_signup')
URL_USERS_LOGIN = lazy_fixture('url_users_login')
URL_USERS_LOGOUT = lazy_fixture('url_users_logout')
URL_COMMENT_DELETE = lazy_fixture('url_comment_delete')
URL_COMMENT_EDIT = lazy_fixture('url_comment_edit')


ANON_CLIENT = lazy_fixture('client')
USER_CLIENT = lazy_fixture('user_client')
AUTHOR_CLIENT = lazy_fixture('author_client')


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    ('url', 'parametrized_client', 'expected_status'),
    (
        (URL_NEWS_HOME, ANON_CLIENT, HTTPStatus.OK),
        (URL_NEWS_DETAIL, ANON_CLIENT, HTTPStatus.OK),
        (URL_USERS_SIGNUP, ANON_CLIENT, HTTPStatus.OK),
        (URL_USERS_LOGIN, ANON_CLIENT, HTTPStatus.OK),
        (URL_USERS_LOGOUT, ANON_CLIENT, HTTPStatus.OK),
        (URL_COMMENT_DELETE, AUTHOR_CLIENT, HTTPStatus.OK),
        (URL_COMMENT_EDIT, AUTHOR_CLIENT, HTTPStatus.OK),
        (URL_COMMENT_DELETE, USER_CLIENT, HTTPStatus.NOT_FOUND),
        (URL_COMMENT_EDIT, USER_CLIENT, HTTPStatus.NOT_FOUND),
    )
)
def test_rooting_for_pages_different_user(
        url, parametrized_client, expected_status, news):
    """Проверка рутинга для страниц для разных пользователей."""
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url', (lazy_fixture('url_comment_delete'),
            lazy_fixture('url_comment_edit'))
)
def test_redirect_for_anon_user(url, url_users_login, client):
    """Проверка редиректов для анонимного пользователя."""
    expected_url = f'{url_users_login}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
