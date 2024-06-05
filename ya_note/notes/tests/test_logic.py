from http import HTTPStatus
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify
from notes.forms import WARNING
from notes.models import Note


class TestCreateNote(TestCase):
    """Тестирование создания заметки."""

    TITLE = 'заголовок_заметки'
    TEXT = 'текст_заметки'
    AUTHOR = 'автор_заметки'
    USER = 'зарегистрированный_пользователь'
    SLUG = 'slug'

    ADD_NOTE_URL = reverse('notes:add')
    NOTE_SUCCESS_URL = reverse('notes:success')

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user = User.objects.create_user(username=cls.USER)
        cls.form_data = {
            'title': cls.TITLE,
            'text': cls.TEXT,
            'slug': cls.SLUG,
        }

    def setUp(self):
        self.auth_client = Client()
        self.auth_client.force_login(self.user)

    def test_anon_user_cannot_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        note_count = Note.objects.count()
        form_data = {
            'title': 'Test Title',
            'text': 'Test Text',
            'slug': 'test-slug'
        }

        self.client.logout()
        self.client.post(reverse('notes:add'), data=form_data)

        final_notes_count = Note.objects.count()
        self.assertEqual(
            note_count,
            final_notes_count,
            'Убедитесь, что анонимный пользователь не может создавать заметки!'
        )

    def test_auth_user_can_create_note(self):
        """
        Проверить, что зарегистрированный пользователь
        может создавать заметку.
        """
        Note.objects.all().delete()
        response = self.auth_client.post(self.ADD_NOTE_URL,
                                         data=self.form_data)

        self.assertRedirects(
            response,
            self.NOTE_SUCCESS_URL,
            msg_prefix=f'Убедитесь, что после заполнения формы создания '
                       f'заметки пользователь перенаправляется на страницу! '
                       f'{self.NOTE_SUCCESS_URL}'
        )
        self.assertEqual(
            Note.objects.count(),
            1,
            f'Проверить, что авторизированный пользователь '
            f'может создать заметку!{self.ADD_NOTE_URL}'
        )

        note = Note.objects.last()
        self.assertEqual(note.title, self.form_data.get('title'),
                         f'Заголовок заметки неверен, {self.ADD_NOTE_URL}')
        self.assertEqual(note.text, self.form_data.get('text'),
                         f'Текст заметки неверен, {self.ADD_NOTE_URL}')
        self.assertEqual(note.slug, self.form_data.get('slug'),
                         f'Slug неверен, {self.ADD_NOTE_URL}')
        self.assertEqual(note.author, self.user, 'Автор неверен')

    def test_slug_auto_generate_from_title_if_the_slug_emty(self):
        """
        Проверить, что slug автоматически генерируется из title,
        если slug не заполнен.
        """
        self.form_data.pop('slug')
        Note.objects.all().delete()
        self.auth_client.post(self.ADD_NOTE_URL, data=self.form_data)
        self.assertEqual(
            Note.objects.count(),
            1,
            'Проверить что слаг генерируется автоматически из title!'
        )
        note = Note.objects.last()
        self.assertEqual(note.title, self.form_data.get('title'),
                         'Заголовок заметки неверен!')
        self.assertEqual(note.text, self.form_data.get('text'),
                         'Текст заметки неверен!')
        self.assertEqual(
            note.slug,
            slugify(note.title),
            'Убедитесь, что slug формируется автоматически из title.'
        )
        self.assertEqual(note.author, self.user, 'Автор неверен!')

    def test_unique_slug(self):
        """Проверить, что невозможно создать две заметки с одинаковым slug."""
        Note.objects.create(author=self.user, **self.form_data)
        note_count = Note.objects.count()
        response = self.auth_client.post(
            self.ADD_NOTE_URL,
            data=self.form_data
        )
        self.assertFormError(
            response,
            'form',
            'slug',
            errors=self.form_data.get('slug') + WARNING,
            msg_prefix='Убедитесь, что нельзя создать две заметки с '
                       'одинаковым slug!'
        )
        self.assertEqual(
            Note.objects.count(),
            note_count,
            'Убедитесь, что нельзя создать две заметки с одинаковым slug!'
        )


class TestNoteEdit(TestCase):
    """Тестирование редактирования заметки."""

    NOTE_TITLE = 'заголовок_заметки'
    NEW_NOTE_TITLE = 'новый_заголовок_заметки'
    NOTE_TEXT = 'текст_заметки'
    NEW_NOTE_TEXT = 'новый_текст_заметки'
    SLUG = 'slug'
    NEW_SLUG = 'new_slug'
    AUTHOR = 'автор_заметки'
    USER = 'зарегистрированный_пользователь'

    SUCCESS_URL = reverse('notes:success')
    EDIT_URL = reverse('notes:edit', args=(SLUG,))
    DELETE_URL = reverse('notes:delete', args=(SLUG,))

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username=cls.AUTHOR)
        cls.user = User.objects.create(username=cls.USER)
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            author=cls.author,
            slug=cls.SLUG
        )
        cls.form_data = {'title': cls.NEW_NOTE_TITLE,
                         'text': cls.NEW_NOTE_TEXT,
                         'author': cls.author,
                         'slug': cls.NEW_SLUG}

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.user_client = Client()
        self.user_client.force_login(self.user)

    def test_author_can_delete_note(self):
        """Проверить, что пользователь может удалять свои заметки."""
        note_count = Note.objects.count()
        response = self.author_client.delete(self.DELETE_URL)

        self.assertRedirects(response, self.SUCCESS_URL,
                             msg_prefix=f'Пользователь перенаправлен на '
                             f'страницу успешного удаления {self.SUCCESS_URL}')
        self.assertEqual(Note.objects.count(), note_count - 1,
                         'Убедитесь, что заметка удалена!')

    def test_user_cant_delete_note_of_another_user(self):
        """Проверить, что пользователь не может удалять чужие заметки"""
        note_count = Note.objects.count()
        self.user_client.delete(self.DELETE_URL)
        self.assertEqual(Note.objects.count(), note_count,
                         'Убедитесь, что заметка не удалена!')

    def test_author_can_edit_note(self):
        """Проверить, что пользователь может редактировать свои заметки."""
        note_count = Note.objects.count()
        response = self.author_client.post(self.EDIT_URL, data=self.form_data)
        self.assertRedirects(
            response,
            self.SUCCESS_URL,
            msg_prefix=f'Убедитесь, что после редактирования заметки '
                       f'пользователь перенаправляется на страницу.'
                       f'{self.SUCCESS_URL}'
        )
        update_note = Note.objects.get()
        self.assertEqual(update_note.slug, self.form_data.get('slug'),
                         'Slug неверен!')
        self.assertEqual(update_note.text, self.form_data.get('text'),
                         'Текст неверен!')
        self.assertEqual(update_note.title, self.form_data.get('title'),
                         'Заголовок неверен!')
        self.assertEqual(update_note.author, self.form_data.get('author'),)
        self.assertEqual(Note.objects.count(), note_count)

    def test_user_cant_edit_note_of_another_user(self):
        """Проверить, что пользователь не может редактировать чужие заметки."""
        note_count = Note.objects.count()
        response = self.user_client.post(self.EDIT_URL, data=self.form_data)
        self.assertEqual(
            response.status_code,
            HTTPStatus.NOT_FOUND,
            'Убедитесь, что заметка не доступна для редактирования '
            'не автором заметки!'
        )
        self.assertEqual(
            note_count,
            1,
            'Убедитесь, что заметка создана и она одна!'
        )
        note = Note.objects.get()
        self.assertEqual(note.title, self.note.title, 'Заголовок неверен!')
        self.assertEqual(note.text, self.note.text, 'Текст неверен!')
        self.assertEqual(note.slug, self.note.slug, 'Slug неверен!')
        self.assertEqual(note.author, self.note.author, 'Автор неверен!')
