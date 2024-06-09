from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note


class TestContent(TestCase):
    """Тестирование контента приложения 'Заметки'."""

    TITLE = 'заголовок_заметки'
    TEXT = 'текст_заметки'
    AUTHOR = 'автор_заметки'
    USER = 'зарегистрированный_пользователь'
    SLUG = 'slug'

    NOTE_LIST_URL = reverse('notes:list')
    ADD_NOTE_URL = reverse('notes:add')
    EDIT_NOTE_URL = reverse('notes:edit', args=(SLUG,))

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(username=cls.AUTHOR)
        cls.user = User.objects.create_user(username=cls.USER)
        cls.note = Note.objects.create(title=cls.TITLE, text=cls.TEXT,
                                       author=cls.author, slug=cls.SLUG)
        cls.reader_note = Note.objects.create(title='reader_title',
                                              text='reader_text',
                                              author=cls.user,
                                              slug='reader_slug')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)

    def test_notes_contain_notes_from_one_author(self):
        """
        Проверить, что список заметок должен содержать
        только заметки одного автора.
        """
        response = self.user_client.get(self.NOTE_LIST_URL)
        object = response.context['object_list']
        self.assertNotIn(
            self.note,
            object,
            'Проверьте, что все заметки текущего'
            'пользователя есть в списке заметок!'
        )

    def test_author_note_appears_on_the_notes_list_page(self):
        """
        Проверить, что заметка автора отображается
        на странице списка заметок.
        """
        initial_count = Note.objects.filter(author=self.author).count()
        response = self.author_client.get(self.NOTE_LIST_URL)
        notes = response.context['object_list']
        final_count = notes.count()

        self.assertEqual(
            final_count,
            initial_count,
            'Проверьте, что заметка автора передаётся на страницу со '
            'списком заметок в списке object_list в словаре context!'
        )
        note = notes[0]
        self.assertEqual(note.author, self.note.author, 'Автор неверен!')
        self.assertEqual(note.slug, self.note.slug, 'Slug заметки неверен!')
        self.assertEqual(note.title, self.note.title, 'Неверный заголовок!')
        self.assertEqual(note.text, self.note.text, 'Текст заметки неверен!')

    def test_note_creation_and_editing_pages_transferred_on_form(self):
        """
        Проверить, что страницы создания и
        редактирования заметки передаются формы.
        """
        urls = (self.ADD_NOTE_URL, self.EDIT_NOTE_URL)
        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
