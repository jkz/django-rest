import re
import json

from django.test import TestCase, Client
from conf import urls

from rest.resources import Resource, Subresource

import rest.resources

from . import models


class Author(Resource):
    model = models.Author

    class Template:
        fields = ['name']

class Book(Resource):
    model = models.Book
    name = 'books'
    uid_field = 'isbn'

    class Template:
        fields = ['isbn', 'title', 'author']
        aliases = {'book_title': 'title'}
        related = {
            'author': Author,
        }

class AuthorBook(Subresource, Book):
    sub_name = 'books'
    rel_field = 'author'
    rel_class = Author

urls.urlpatterns += Book.urls()
urls.urlpatterns += Author.urls()
urls.urlpatterns += AuthorBook.urls()


class ResourceTestCase(TestCase):
    def test_name(self):
        self.assertEqual(Book.get_name(), 'books')

    def test_get_ids(self):
        isbn = 'ABC123'

        books = Book(uid=isbn)

        self.assertEqual(books.ids, {'uid': isbn})
        self.assertEqual(books.get_ids(), {'isbn': isbn})
        self.assertEqual(books.data, {})
        self.assertEqual(books.get_data(), {'isbn': isbn})

    def test_parse_body(self):
        body = '{"author": 1, "title": "Title"}'

        books = Book()
        books.parse_body(body)

        self.assertEqual(books.data, {'author': 1, 'title': "Title"})

    def test_parse_query(self):
        query = {'limit': '5', 'offset': '0'}

        books = Book()
        books.parse_query(**query)

        self.assertEqual(books.query, query)

    def test_uid_field(self):
        class Book2(Book):
            uid_field = 'isbn'

        books1 = Book()
        books2 = Book2()
        authorbooks = AuthorBook()

        self.assertEqual(books1.get_uid_field(), 'isbn')
        self.assertEqual(books2.get_uid_field(), 'isbn')
        self.assertEqual(authorbooks.get_uid_field(), 'isbn')

    def test_rel_field(self):
        class AuthorBook2(AuthorBook):
            rel_field = 'author'

        authorbooks1 = AuthorBook()
        authorbooks2 = AuthorBook2()

        self.assertEqual(authorbooks1.get_rel_field(), 'author')
        self.assertEqual(authorbooks2.get_rel_field(), 'author')

    def test_location(self):
        isbn = 'ABC123'
        author = 1

        books1 = Book()
        books2 = Book(ids={'uid': isbn})

        authorbooks1 = AuthorBook(ids={'rel': author})
        authorbooks2 = AuthorBook(ids={'rel': author, 'uid': isbn})

        self.assertEqual(books1.location(), '/books')
        self.assertEqual(books2.location(), '/books/ABC123')
        self.assertEqual(authorbooks1.location(), '/authors/1/books')
        self.assertEqual(authorbooks2.location(), '/authors/1/books/ABC123')

    def test_body(self):
        book = Book()
        book.parse_body('{"title": "I\'m in wonderland"}')

        self.assertEqual(book.data, {'title': "I'm in wonderland"})

    def test_urls(self):
        books = tuple(b.regex.pattern for b in Book().urls())
        authorbooks = tuple(b.regex.pattern for b in AuthorBook().urls())

        self.assertEqual(books, (
            'books$',
            'books/(?P<uid>[^/]+)$'))
        self.assertEqual(authorbooks, (
            'authors/(?P<rel>[^/]+)/books$',
            'authors/(?P<rel>[^/]+)/books/(?P<uid>[^/]+)$'))


    def test_template(self):
        book = Book()

        self.maxDiff = None

        check = {
            'fields': ['isbn', 'title', 'author'],
            'aliases': {'book_title': 'title'},
            'related': {
                'author': {
                    'fields': ['name'],
                }
            }
        }

        self.assertEqual(book.template(), check)


    def test_request(self):
        name = 'jan'
        isbn = 'ABC123'
        title = 'Title'

        author = models.Author.objects.create(name=name)
        book = author.book_set.create(isbn=isbn, title=title)

        c = Client()
        response = c.get('/books')

        self.assertEqual(response.status_code, 200)

        content = str(response.content, 'utf-8')
        data = json.loads(content)

        check = {
            'data': [
                {
                    'isbn': isbn,
                    'title': title,
                    'author': {
                        'name': name,
                    }
                },
            ],
            'meta': {
                'count': 1,
            },
        }

        self.assertEqual(data, check)

