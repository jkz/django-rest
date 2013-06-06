from django.test import TestCase

from rest import structures

class StructuresTestCase(TestCase):
    def test_updater(self):
        class Updater(structures.Updater):
            def before(self, data):
                return {'amount': 2}
            def after(self, data):
                data['fractal'] = data.copy()
                return data
            def foo(self, data):
                return data['amount'] * 'foo'
            def bar(self, data):
                return 'bar'

        updater = Updater()
        data = updater()
        result = {'amount': 2, 'foo': 'foofoo', 'bar': 'bar'}
        result['fractal'] = result.copy()
        self.assertEqual(data, result)

    def test_reducer(self):
        class Reducer(structures.Reducer):
            def before(self, queryset, **query):
                return queryset + [2]

            def append(self, queryset, val):
                return queryset + [val]

            def after(self, queryset, **query):
                return 2 * queryset

        case = Reducer()([1], append='foo')
        check = [1, 2, 'foo', 1, 2, 'foo']
        self.assertEqual(case, check)

    def test_mapper(self):
        class Mapper(structures.Mapper):
            def before(self, resource, **options):
                resource['before'] = None

            def foo(self, resource, val):
                resource['foo'] = True

            def after(self, resource, **options):
                resource['after'] = False

        resource = {}

        case = Mapper()(resource, foo=None)
        check = {'before': None, 'foo': True, 'after': False}

        self.assertEqual(resource, check)

