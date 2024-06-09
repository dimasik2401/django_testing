from http import HTTPStatus

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from notes.models import Note


class TestRoutes(TestCase):
    """Тестирование роуминга приложения 'Заметки'."""

    AUTHOR = 'автор_заметки'
    USER = 'зарегистрированный_пользователь'
    TITLE = 'заголовок_заметки'
    TEXT = 'текст_заметки'
    SLUG = 'slug'

    USERS_LOGIN_URL = reverse('users:login')
    USERS_LOGOUT_URL = reverse('users:logout')
    USERS_SIGNUP_URL = reverse('users:signup')
    NOTES_HOME_URL = reverse('notes:home')
    NOTES_ADD_URL = reverse('notes:add')
    NOTES_LIST_URL = reverse('notes:list')
    NOTES_SUCCESS_URL = reverse('notes:success')
    NOTES_EDIT_URL = reverse('notes:edit', args=(SLUG,))
    NOTES_DETAIL_URL = reverse('notes:detail', args=(SLUG,))
    NOTES_DELETE_URL = reverse('notes:delete', args=(SLUG,))

    urls = (
        NOTES_HOME_URL,
        NOTES_EDIT_URL,
        NOTES_DETAIL_URL,
        NOTES_DELETE_URL,
        NOTES_ADD_URL,
        NOTES_LIST_URL,
        NOTES_SUCCESS_URL,
        USERS_LOGIN_URL,
        USERS_SIGNUP_URL,
        USERS_LOGOUT_URL,
    )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username=cls.AUTHOR)
        cls.user = User.objects.create_user(username=cls.USER)
        cls.note = Note.objects.create(
            title=cls.TITLE,
            text=cls.TEXT,
            slug=cls.SLUG,
            author=cls.author,
        )

        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)

    def test_page_for_author(self):
        """Проверка доступности страниц для пользователя автора."""
        for url in self.urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_page_for_user(self):
        """Проверка доступности страниц для пользователя."""
        urls_not_available_for_user = (
            self.NOTES_EDIT_URL, self.NOTES_DELETE_URL, self.NOTES_DETAIL_URL
        )
        for url in self.urls:
            response = self.user_client.get(url)
            with self.subTest(url=url):
                expected_status_code = (HTTPStatus.NOT_FOUND
                                        if url in urls_not_available_for_user
                                        else HTTPStatus.OK)
            self.assertEqual(response.status_code, expected_status_code)

    def test_page_for_anon(self):
        """Проверка доступности страниц для анонимного пользователя."""
        urls_available_for_anon = (
            self.NOTES_HOME_URL, self.USERS_LOGIN_URL,
            self.USERS_SIGNUP_URL, self.USERS_LOGOUT_URL
        )
        for url in self.urls:
            response = self.client.get(url)
            with self.subTest(url=url):
                if url in urls_available_for_anon:
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                else:
                    redirect_url = f'{self.USERS_LOGIN_URL}?next={url}'
                    self.assertRedirects(
                        response,
                        redirect_url,
                        msg_prefix=f'Проверьте что страница {url} не доступна '
                                   'для не зарегистрированного пользователя'
                                   ' и осуществляется редирект на '
                                   f'{redirect_url}'
                    )
