from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note


User = get_user_model()

class TestListPage(TestCase):

    LIST_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        # Создаём заметки по одной, чтобы вызывался save()
        cls.note1 = Note.objects.create(
            title='Первая заметка',
            text='Текст первой заметки',
            author=cls.author
        )
        cls.note2 = Note.objects.create(
            title='Вторая заметка',
            text='Текст второй заметки', 
            author=cls.author
        )
        cls.note3 = Note.objects.create(
            title='Третья заметка',
            text='Текст третьей заметки',
            author=cls.author
        )


    def test_notes_order(self):
        self.client.force_login(self.author)
        response = self.client.get(self.LIST_URL)
        object_list = response.context['object_list']
        all_notes = [note.id for note in object_list]
        sorted_notes = sorted(all_notes)
        self.assertEqual(all_notes, sorted_notes)
