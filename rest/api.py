from . resources import Resource, Subresource
from . import models

from django.models.query import Q

class Author(Resource):
    model = models.Author

    template = {
        'fields': ['id', 'name'],
    }

class Book(Resource):
    model = models.Book

    class Template:
        fields = ['isbn', 'title', 'summary']
        related = {
            'author': Author.template,
        }

    class Option:
        def size(self, resource, size):
            if size == 'mini':
                template = {
                    'fields': ['isbn', 'title'],
                    'related': {
                        'author': {
                            'values_list': True,
                        }
                    }
                }
                resource.template.update(template)
            elif size == 'full':
                pass

    class Filter:
        def tags(self, queryset, tags):
            q = Q()
            for tag in tags.split(','):
                q |= Q(tags__name=tag)
            return queryset.filter(q)

        def child_friendly(self, queryset, flag):
            if flag == 'true':
                queryset = querset.filter(recommended_age__lt=12)
            return queryset

