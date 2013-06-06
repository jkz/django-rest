import json
import functools
import copy
from undjango import undjango

from django.http import HttpRequest
from django.db.models.query import QuerySet
from django.conf.urls import url
from django.core.urlresolvers import reverse

"""
url = QuerySet = HttpRequest = reverse = NotImplemented
"""

from . import exceptions
from . import serializers
from . import validators
from . import structures
from . import slicers
from . import templates


class Cardinality(structures.NestedClass):
    methods = set()

    def __call__(self, resource):
        if resource.method not in self.methods or not hasattr(self, resource.method):
            raise exceptions.MethodNotAllowed() # 504

        return getattr(self, resource.method)(resource)


class One(Cardinality):
    methods = {'GET', 'PUT', 'PATCH', 'DELETE'}

    def GET(self, resource):
        return resource.get_object()

    def PUT(self, resource):
        return resource.update_object(create=True)

    def PATCH(self, resource):
        return resource.update_object()

    def DELETE(self, resource):
        resource.get_object().delete()


class Many(Cardinality):
    methods = {'GET', 'POST', 'DELETE'}

    def GET(self, resource):
        return resource.get_queryset()

    def POST(self, resource):
        return resource.create_obj()

    def DELETE(self, resource):
        objects, meta = resource.get_queryset()
        for obj in objects:
            obj.delete()
        return None, meta


class Resource(object, metaclass=structures.NestingMeta):
    model = None
    queryset = None

    uid_field = 'pk'

    # Defines the actions performed on object collections
    Many = Many

    # Defines the actions performed on single objects
    One = One

    # Slice the queryset for collections
    Slicer = slicers.Slicer

    # Modify the resource options on the object itself by key, value
    # pairs in the query
    Option = structures.Mapper

    # Validates input data before passing it to the database controller
    Validator = validators.Validator

    # Filter the queryset with the query parameters
    Filter = structures.Reducer

    # Process inward data; json to database
    # Modifies a dictionary so it manps to data that can be fed directly
    # into the backend.
    Hydrator = structures.Updater

    # Process outward data; database to json
    # Modifies a dictionary so it contains all data that should be
    # returned to the frontend.
    Dehydrator = structures.Updater

    # Turns the data object into a string
    Serializer = serializers.Serializer

    # The database columns to resource mapper
    Template = templates.Template

    option = structures.cache('Option')
    validate = structures.cache('Validator')
    filter = structures.cache('Filter')
    slice = structures.cache('Slicer')
    hydrate = structures.cache('Hydrator')
    dehydrate = structures.cache('Dehydrator')
    template = structures.cache('Template')
    serialize = structures.cache('Serializer')

    def __init__(self, request=None, ids=None, data=None, query=None,
            method=None, template=None, **url_kwargs):

        self.ids = {}
        self.data = {}
        self.query = {}
        self.method = 'GET'

        if request: self.parse_request(request)
        if url_kwargs: self.parse_url(**url_kwargs)

        if ids: self.ids = ids
        if data: self.data = data
        if query: self.query = query
        if method: self.method = method

        self.request = request or HttpRequest()
        #self.template = template or copy.deepcopy(self.template)

        if self.queryset is not None:
            self.queryset = self.queryset._clone()
            self.model = self.queryset.model
        elif self.model is not None:
            self.queryset = self.model._default_manager.all()
        else:
            raise ImproperlyConfigured("No model or queryset on {}"
                    .format(self.__class__.__name__))

        # Apply options
        self.option(self, **self.query)

    def act(self):
        # Having a unique identifier determines whether to request
        # many objects or one
        actor = self.One() if 'uid' in self.ids else self.Many()

        errors = self.validate(**self.data)
        if errors:
            raise Exception()

        data, meta = actor(self)
        undjangoed = undjango.undjango(data, **self.template())
        dehydrated = self.dehydrate(undjangoed)

        # TODO: make this configurable
        if meta:
            payload = {'data': dehydrated, 'meta': meta}
        else:
            payload = dehydrated

        serialized = self.serialize(payload, format='json') #TODO

        return serialized

    def get_ids(self):
        ids = {}
        if 'uid' in self.ids:
            ids[self.get_uid_field()] = self.ids['uid']
        return ids

    def get_data(self):
        data = copy.deepcopy(self.data)
        data.update(self.get_ids())
        data = self.hydrate(data)
        return data

    def get_queryset(self):
        # Filter on super resource ids
        original = self.queryset.filter(**self.get_ids())

        # Apply conditional filters
        filtered = self.filter(original, **self.query)

        # Paginate the result set
        sliced, meta = self.slice(self, filtered)

        return sliced, meta

    def get_object(self):
        data = self.get_data()
        return self.queryset.get(**data), None

    def update_object(self, create=False):
        data = self.get_data()
        obj = self.model(**data)
        if create:
            obj.save(update_fields=data.keys())
        else:
            obj.save()
        return obj

    def create_object(self):
        data = self.get_data()
        data.pop(self.get_uid_field())
        obj = self.model(**data)
        obj.save()
        return obj

    def location(self):
        #XXX This does not desubresource yet
        return reverse(self.get_full_name(), kwargs=self.ids)
        return reverse(self.get_name(), kwargs=self.ids)

    def parse_method(self, method):
        self.method = method.upper()

    def parse_body(self, body):
        if body:
            self.data.update(json.loads(body))

    def parse_query(self, **query):
        self.query.update(query)

    def parse_url(self, **kwargs):
        self.ids = kwargs

    def parse_request(self, request):
        self.parse_method(request.method)
        self.parse_body(request.body)
        self.parse_query(**request.GET.dict())

    @classmethod
    def get_name(cls):
        return getattr(cls, 'name', cls.__name__.lower() + 's')

    @classmethod
    def get_full_name(cls):
        return cls.get_name()

    @classmethod
    def get_uid_field(cls):
        #XXX Trying with name
        if hasattr(cls.uid_field, 'name'):
            return cls.uid_field.name
        elif cls.uid_field == 'pk':
            return cls.model._meta.pk.name
        else:
            return cls.uid_field
        #XXX maybe this should be name in stead of db_column
        if hasattr(cls.uid_field, 'db_column'):
            return cls.uid_field.db_column
        elif cls.uid_field == 'pk':
            return cls.model._meta.pk.db_column
        else:
            return cls.uid_field

    @classmethod
    def view(cls, request, **kwargs):
        return cls(request, **kwargs).act()

    @classmethod
    def urls(cls):
        name = cls.get_full_name()
        base = cls.get_name()
        return (
            url(base + '$', cls.view, name=name),
            url(base + '/(?P<uid>[^/]+)$', cls.view, name=name)
        )


class Subresource(Resource):
    """
    Represents a resource that references another resource class with a
    sepcified field.
    """
    # The field on this resources model that references another resource
    rel_field = NotImplemented

    # The resource class of the referenced other resource
    rel_class = NotImplemented

    def get_ids(self):
        ids = super().get_ids()
        if 'rel' in self.ids:
            ids[self.get_rel_field()] = self.ids['rel']
        return ids

    @classmethod
    def get_full_name(cls):
        return '{}__{}'.format(cls.rel_class.get_name(), cls.get_name())

    @classmethod
    def get_rel_name(cls):
        if hasattr(cls.rel_class, 'get_name'):
            return cls.rel_class.get_name()
        else:
            return cls.rel_class

    @classmethod
    def get_rel_field(cls):
        if hasattr(cls.rel_field, 'db_column'):
            return cls.rel_field.db_column
        else:
            return cls.rel_field

    @classmethod
    def urls(cls):
        name = cls.get_full_name()
        base = '{}/(?P<rel>[^/]+)/{}'.format(cls.get_rel_name(), cls.get_name())
        return (
            url(base + '$', cls.view, name=name),
            url(base + '/(?P<uid>[^/]+)$', cls.view, name=name),
        )

