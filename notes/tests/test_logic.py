from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()

class TestNoteCreate(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='test_ser_one')
        cls.another_user = User.objects.create(username='test_ser_two')
        cls.note_user = Note.objects.create(
            text='text',
            title='Заметка пользователя 1',
            author = cls.user,
            slug = 'user-note-1'
        )
        cls.note_another_user = Note.objects.create(
            text='text',
            title='Заметка пользователя 2',
            author = cls.another_user,
            slug = 'user-note-2'
        )

        cls.add_url = reverse('notes:add')
        cls.edit_url_user = reverse('notes:edit', args=(cls.note_user.slug,))
        cls.delete_url_user = reverse('notes:delete', args=(cls.note_user.slug,))
        cls.edit_url_another = reverse('notes:edit', args=(cls.note_another_user.slug,))
        cls.delete_url_another = reverse('notes:delete', args=(cls.note_another_user.slug,))


    def test_authorized_user_can_create_note(self):
        """Авторизованный пользователь может создать заметку."""
        self.client.force_login(self.user)
        response = self.client.get(self.add_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_user_can_delete_own_note(self):
        """Автор может удалить свою заметку."""
        self.client.force_login(self.user)
        response = self.client.get(self.delete_url_user)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_user_can_edit_own_note(self):
        """Автор может редактировать свою заметку."""
        self.client.force_login(self.user)
        response = self.client.get(self.edit_url_user)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_user_cannot_edit_another_note(self):
        """Пользователь не может редактировать чужую заметку."""
        self.client.force_login(self.user)
        response = self.client.get(self.edit_url_another)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_user_cannot_delete_another_note(self):
        """Пользователь не может удалить чужую заметку."""
        self.client.force_login(self.user)
        response = self.client.get(self.delete_url_another)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_auto_slug_generation(self):
        """Если при создании заметки не заполнен slug, он формируется автоматически."""
        self.client.force_login(self.user)
        add_url = reverse('notes:add')
        
        # Создаем заметку без slug
        form_data = {
            'title': 'Тестовая заметка без slug',
            'text': 'Текст заметки'
            # slug не передаем
        }
        response = self.client.post(add_url, data=form_data)
        
        # Проверяем, что заметка создалась с автоматическим slug
        note = Note.objects.get(title='Тестовая заметка без slug')
        self.assertIsNotNone(note.slug)
        self.assertTrue(len(note.slug) > 0)

    def test_duplicate_slug_prevention(self):
        """Невозможно создать две заметки с одинаковым slug."""
        self.client.force_login(self.user)
        add_url = reverse('notes:add')
        
        # Пытаемся создать заметку с существующим slug
        form_data = {
            'title': 'Новая заметка',
            'text': 'Текст',
            'slug': 'user-note-1'  # slug уже существует
        }
        response = self.client.post(add_url, data=form_data)
        
        # Должна вернуться ошибка формы
        self.assertIn('form', response.context)
        self.assertFalse(response.context['form'].is_valid())

    def test_anonymous_user_cannot_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        add_url = reverse('notes:add')
        
        # GET запрос - должен перенаправить на логин
        response = self.client.get(add_url)
        self.assertNotEqual(response.status_code, HTTPStatus.OK)
        
        # POST запрос - тоже должен перенаправить
        form_data = {
            'title': 'Анонимная заметка',
            'text': 'Текст'
        }
        response = self.client.post(add_url, data=form_data)
        self.assertNotEqual(response.status_code, HTTPStatus.OK)