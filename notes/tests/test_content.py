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

    def test_forms_on_pages(self):
        """На страницы создания и редактирования заметки передаются формы."""
        self.client.force_login(self.author)
        
        # Проверка формы на странице создания
        add_url = reverse('notes:add')
        response = self.client.get(add_url)
        self.assertIn('form', response.context)
        
        # Проверка формы на странице редактирования
        edit_url = reverse('notes:edit', args=(self.note1.slug,))
        response = self.client.get(edit_url)
        self.assertIn('form', response.context)

    def test_notes_isolation(self):
        """В список заметок одного пользователя не попадают заметки другого пользователя."""
        # Создаем второго пользователя и его заметку
        other_user = User.objects.create(username='other_user')
        Note.objects.create(
            title='Чужая заметка',
            text='Текст чужой заметки',
            author=other_user
        )
        
        # Логиним первого пользователя
        self.client.force_login(self.author)
        response = self.client.get(self.LIST_URL)
        object_list = response.context['object_list']
        
        # Проверяем, что в списке только заметки автора
        author_notes_ids = [note.id for note in object_list]
        all_notes_ids = list(Note.objects.values_list('id', flat=True))
        
        # У автора должно быть меньше заметок, чем всего в базе
        self.assertLess(len(author_notes_ids), len(all_notes_ids))
        
        # Или проверяем конкретно по авторам
        for note in object_list:
            self.assertEqual(note.author, self.author)