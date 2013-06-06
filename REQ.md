Filosophy
=========
Main goals for this REST framework:
* enforce best practices
* minimize boilerplate / clean api
* minimize complexity
* modular resource configuration

Best practices
==============
http://pydanny.com/choosing-an-api-framework-for-django.html

What makes a decent API Framework?
These features:

pagination
----------
limit
offset
before
after
ubefore
uafter

DRAFT 1:
Just limit and offset
Entire collections are browsable in chunks of `limit` size
When offset > 0, add a `prev` link
When query count == limit add a `next`

DRAFT 2:
page + size
offset is calculated by page * size

posting of data with validation
-------------------------------
validators on fields, perhaps forms framework

Publishing of metadata along with querysets
-------------------------------------------

API discovery
-------------
HATEOAS
- pagination links
'meta': {
    'count': 10,
    'prev': 'http://resour.ce/objects/?limit=10&offset=1,
    'next': 'http://resour.ce/objects/?limit=10&offset=3,

    'summary': 'http://resour.ce/objects/123456/?full=false',
    'full': 'http://resour.ce/objects/123456/?full=true',

    'nested': 'http://resour.ce/objects/123456/?chatty=false
    'chatty': 'http://resour.ce/objects/123456/?chatty=true
}

'book': {
    'rel': 'book',
    'url': 'http://resour.ce/books/123456/?full=true',
}


proper HTTP response handling
-----------------------------
GET, POST, PUT, DELETE etc


caching

serialization
-------------
json only
django serializaton / preserialize-like framework


throttling

authentication
--------------
Use any django authentication backend.

permissions
-----------
Resources can specify custom authorisation functions to check if a user can
perform an action



Proper API frameworks also need:

Really good test coverage of their code
Decent performance
Documentation
An active community to advance and support the framework


API
===
# resources.py
from . import models
from .decorators import resource

class Book(Resource):
    name = 'books'
    model = models.Book
    identifier = 'isbn'

@resource(models.Author)
class Author:
    pass

@subresource('authors', 'books', 'novels')
class AuthorBook:


@resource(models.Book, 'novels')
class Book:
    # Serialization configuration template
    template = {
        'fields': ['pk', 'title'],
        'related': ['author'],
    }

    # Filters are simple alterations applied to the collection just before it
    # is issued to the database
    class Collection(Collection):
        # Define query filters for collections
        def min_pages(self, val):
            return self.filter(pages__gte=int(val))

        def max_pages(self, val):
            return self.filter(pages__lte=int(val))

        def tags(self, val):
            return self.filter(tag__in=val.split(',')

    # Filters are applied when the data has been fetched, before it is
    # undjangoed.


Provide several hooks for custom processing and query dependent behaviour


Minimize Complexity
=======
URL structure

Use plural resource names

?tags=kitten,cake&max_pages=200

{scheme}://{domain}/{api}/{resource}/
GET - List entries matching query
DELETE - Delete entries matching query
POST - Add new entry/entries

{scheme}://{domain}/{api}/{resource}/{uid}/
GET - Return specific entry
PUT - Create or update specific resource
DELETE - Delete specific entry

{scheme}://{domain}/{api}/{resource}/{rel}/{related}/
GET - List related entries matching query
POST - Add related entry/entries
DELETE - Delete related entries matching query

{scheme}://{domain}/{api}/{resource}/{rel}/{related}/{uid}/
GET - Return specific related entry
PUT - Create or update specific related entry
DELETE - Delete specific related entry

Responses
---------
DELETE
# 200 Success
# 202 Accepted (but pending)
# 204 No Content
