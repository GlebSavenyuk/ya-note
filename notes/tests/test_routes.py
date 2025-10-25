from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()

class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Создаем двух пользователей
        cls.author = User.objects.create(username='author')
        cls.other_user = User.objects.create(username='other_user')

        # Создаем заметку от имени автора
        cls.note = Note.objects.create(
            title='Моя первая заметка',
            text='Текст',
            author=cls.author
        )


    def test_home_page(self):
        """Главная страница доступна всем."""
        url = reverse('notes:home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)


    def test_note_detail_author_access(self):
        """Автор может просматривать свою заметку."""
        self.client.force_login(self.author)
        url = reverse('notes:detail', args=(self.note.slug,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)


    def test_note_detail_other_user_access(self):
        """Другой пользователь НЕ может просматривать чужую заметку."""
        self.client.force_login(self.other_user)
        url = reverse('notes:detail', args=(self.note.slug,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)


    def test_redirect_for_anonymous_on_protected_pages(self):
        """Анонимы перенаправляются на логин при доступе к защищенным страницам."""
        protected_urls = (
            ('notes:add', None),
            ('notes:list', None),
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        )
        
        login_url = reverse('users:login')
        
        for name, args in protected_urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                redirect_url = f'{login_url}?next={url}'
                self.assertRedirects(response, redirect_url)


    def test_pages_availability(self):
        """Тестируем доступность всех типов страниц."""
        # Публичные страницы
        public_urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:signup', None),
        )
        
        # Страницы только для авторизованных
        authenticated_urls = (
            ('notes:add', None),
            ('notes:list', None),
            ('notes:success', None),
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        )

        # Тестируем публичные страницы
        for name, args in public_urls:
            with self.subTest(category='public', name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

        # Тестируем страницы для авторизованных
        self.client.force_login(self.author)
        for name, args in authenticated_urls:
            with self.subTest(category='authenticated', name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)


    def test_note_edit_delete_access(self):
        """Тестируем доступ к редактированию и удалению заметок."""
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.other_user, HTTPStatus.NOT_FOUND),
        )
        
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:edit', 'notes:delete'):
                with self.subTest(user=user.username, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)