from datetime import timedelta

import pytest
from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    """Фикстура для создания автора."""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def user(django_user_model):
    """Фикстура для создания пользователя."""
    return django_user_model.objects.create(username='Пользователь')


@pytest.fixture
def url_news_home():
    """Фикстура главной страницы."""
    return reverse('news:home')


@pytest.fixture
def url_news_detail(news):
    """Фикстура одной новости страницы."""
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def url_users_signup():
    """Фикстура страницы регистрации."""
    return reverse('users:signup')


@pytest.fixture
def url_users_login():
    """Фикстура страницы входа."""
    return reverse('users:login')


@pytest.fixture
def url_users_logout():
    """Фикстура страницы выхода."""
    return reverse('users:logout')


@pytest.fixture
def url_comment_delete(comment):
    """Фикстура страницы удаления комментария."""
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def url_comment_edit(comment):
    """Фикстура страницы редактирования комментария."""
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def author_client(author):
    """Фикстура для создания клиента с автором."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def user_client(user):
    """Фикстура для создания клиента с пользователя не автор."""
    client = Client()
    client.force_login(user)
    return client


@pytest.fixture
def news():
    """Фикстура для создания новости."""
    news = News.objects.create(
        title='Заголовок_новости',
        text='Текст_новости',
    )
    return news


@pytest.fixture
def comment(author, news):
    """Фикстура для создания комментария к новости пользователем автор."""
    comment = Comment.objects.create(
        news_id=news.id,
        author_id=author.id,
        text='Текст_комментария',
    )
    return comment


@pytest.fixture
def news_for_main_page():
    """Фикстура для создания новостей."""
    today = timezone.now()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)


@pytest.fixture
def comments_for_same_news(author, news):
    """Фикстура для создания 2 комментариев к одной новости."""
    for index in range(2):
        Comment.objects.create(
            news_id=news.id,
            author_id=author.id,
            text=f'Текст_комментария{index}',
        )


@pytest.fixture
def form_data():
    """Фикстура для создания формы комментария."""
    return {
        'text': 'Новый_текст_комментария',
    }
