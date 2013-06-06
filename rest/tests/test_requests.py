import json

from django.test import TestCase, Client

from rest import resources
from conf import urls

from . import models

class Person(resources.Resource):
    model = models.Person

    class Template:
        fields = ['name', 'age']

class Comment(resources.Subresource):
    model = models.Comment

    class Template:
        related = {
            'person': {
                'fields': ['name'],
            },
        }

    class Dehydrator:
        def timestamp(self, data):
            return str(data['timestamp'])


class Image(resources.Resource):
    model = models.Image

    class Template:
        related = {
            'owner': Person,
            'comment_set': Comment,
            'tags': {
                'values_list': True,
                'fields': ['name'],
            }
        }

    class Filter:
        def tags(self, queryset, tags):
            return queryset.filter(tag__name__in=tags.split(','))

    class Dehydrator:
        def timestamp(self, data):
            return str(data['timestamp'])

class PersonImage(resources.Subresource, Image):
    rel_class = Person
    rel_field = 'person'

    class Filter:
        def adult(self, queryset, flag):
            if flag == 'true':
                queryset = queryset.filter(age__gte=18)
            return queryset

urls.urlpatterns += Image.urls()
urls.urlpatterns += Person.urls()
urls.urlpatterns += PersonImage.urls()

class RequestTestCase(TestCase):
    def test_request(self):
        persons = [
            models.Person.objects.create(name='person1', age=10),
            models.Person.objects.create(name='person2', age=20),
            models.Person.objects.create(name='person3', age=30),
        ]

        images = [
            persons[0].image_set.create(title='image1', url='/image1.jpg'),
            persons[0].image_set.create(title='image2', url='/image2.jpg'),
            persons[1].image_set.create(title='image3', url='/image3.jpg'),
            persons[1].image_set.create(title='image4', url='/image4.jpg'),
            persons[1].image_set.create(title='image5', url='/image5.jpg'),
            persons[2].image_set.create(title='image6', url='/image6.jpg'),
        ]

        comments = [
            images[0].comment_set.create(person=persons[1], text='comment1'),
            images[0].comment_set.create(person=persons[2], text='comment2'),
            images[0].comment_set.create(person=persons[1], text='comment3'),
            images[1].comment_set.create(person=persons[0], text='comment4'),
        ]

        c = Client()
        response = c.get('/images?offset=2&limit=2')
        content = str(response.content, 'utf-8')
        data = json.loads(content)
        self.assertEqual(len(data['data']), 2)

        response = c.get('/images/3')
        content = str(response.content, 'utf-8')
        data = json.loads(content)
        self.assertEqual(data['url'], '/image3.jpg')


