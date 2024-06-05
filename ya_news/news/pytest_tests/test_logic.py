import pytest
from http import HTTPStatus
from pytest_django.asserts import assertFormError, assertRedirects
from news.forms import BAD_WORDS, WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db


def test_create_comment_with_bad_words(user_client, news, url_news_detail):
    """Проверить, что нельзя писать в комментарии запрещенные слова."""
    count_comments = Comment.objects.count()
    bad_words_data = {'text': f'{BAD_WORDS}...'}
    response = user_client.post(url_news_detail, data=bad_words_data)
    assert Comment.objects.count() == count_comments
    assertFormError(response, form='form', field='text', errors=WARNING)


def test_author_can_edit_and_delete_comment(
        author_client, comment, form_data, url_comment_edit,
        url_comment_delete, url_news_detail, author, news):
    """Проверить, что автор может редактировать и удалять свои комментарии."""
    count_comments = Comment.objects.count()
    response_edit = author_client.post(url_comment_edit, form_data)
    assertRedirects(response_edit, f'{url_news_detail}#comments')
    assert Comment.objects.count() == count_comments
    new_comment = Comment.objects.last()
    assert new_comment.text == form_data['text']
    assert new_comment.author == comment.author
    assert new_comment.news == comment.news

    response_delete = author_client.post(url_comment_delete)
    assertRedirects(response_delete, f'{url_news_detail}#comments')
    assert Comment.objects.count() == count_comments - 1


def test_user_cannot_edit_or_delete_other_comments(
        user_client, comment, form_data, url_comment_edit, url_comment_delete,
        author, news):
    """
    Проверить, что пользователь не может редактировать
    или удалять чужие комментарии.
    """
    count_comments = Comment.objects.count()
    response_edit = user_client.post(url_comment_edit, form_data)
    assert response_edit.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == count_comments
    new_comment = Comment.objects.last()
    assert new_comment.text == comment.text
    assert new_comment.author == author
    assert new_comment.news == news

    response_delete = user_client.post(url_comment_delete)
    assert response_delete.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == count_comments


def test_unauthorized_user_cannot_leave_comments(
        client, news, form_data, url_news_detail, url_users_login):
    """
    Проверить, что неавторизированный пользователь
    не может публиковать комментарии.
    """
    count_comments = Comment.objects.count()
    response = client.post(url_news_detail, data=form_data)
    assertRedirects(response, f'{url_users_login}?next={url_news_detail}')
    assert Comment.objects.count() == count_comments


def test_authorized_can_leave_comments(
        user_client, news, form_data, url_news_detail, user, author):
    """
    Проверить, что авторизированный пользователь
    может оставлять комментарии.
    """
    count_comments = Comment.objects.count()
    response = user_client.post(url_news_detail, data=form_data)
    assertRedirects(response, f'{url_news_detail}#comments')
    assert Comment.objects.count() == count_comments + 1
    new_comment = Comment.objects.last()
    assert new_comment.text == form_data['text']
    assert new_comment.author == user
    assert new_comment.news == news
