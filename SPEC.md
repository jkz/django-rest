We specify a Resource class

    # resources.py
    from . import models

    class Book(Resource):
        model = models.Book

        # These classes extend their bases automatically
        class Object:

        class Collection:

        # These attributes are triggered by query parameters
        #
        # example:
        # /resources/123/?short=true
        class Filter:
            def q(self, queryset, val):
                """Do search stuff!"""
                return queryset.all()

            def tags(self, queryset, val):
                tags = val.split(',')
                return queryset.filter(tag__name__in=tags)

        class Options:
            def short(self, request, val):
                val = val == 'true'


Request stages:

    Parse request
    - extract parameters from headers
        + meta
        + format
        + auth
    ##########################
    - extract parameters from url
        + resource
        + uid
    - extract parameters from query (GET, DELETE)
        + filter(queryset, val)
        + options(resource, val)
    - extract parameters from body (PUT, POST)
        + object data


    Collection:
        Retrieve queryset
        Filter queryset
            def color(queryset, val):
                return queryset.filter(color=val)
        Slice queryset

    Object:
        Retrieve object


    Serialize



    object
    {
        "id": "123456",
        "name": "Some Name",
        "href": "http://resour.ce/feed/123",
        "text": "I am going to look the moon, brb",

        "user": {
            "id": "1",
            "name": "Jack",
            "href": "http://resour.ce/users/1",
        },

        "responses": {
            "href": "http://resour.ce/posts/123/responses",
            "links": {
                "next": "http://resour.ce/posts/123/?offset=3&limit=3"
            }
            "items": [
                {
                    "id": "1",
                    "text": "Boo",
                    "href": "http://resour.ce/posts/123/responses/1",
                    "user": {
                        "id": "2",
                        "name": "Bob",
                        "href": "http://resour.ce/users/2",
                    }
                    "date": "somethingsomething".
                },
                {
                    "id": "2",
                    "text": "Yay",
                    "href": "http://resour.ce/posts/123/responses/2",
                    "user": {
                        "id": "3",
                        "name": "Lisa",
                        "href": "http://resour.ce/users/3",
                    }
                    "date": "somethingsomething".
                },
                {
                    "id": "3",
                    "text": "Meh",
                    "href": "http://resour.ce/posts/123/responses/3",
                    "user": {
                        "id": "4",
                        "name": "Frank",
                        "href": "http://resour.ce/users/4",
                    }
                    "date": "somethingsomething".
                },
            ]
        }
    }


    collection
    {
        "href": "http://resour.ce/thingy/"

        "links": {
            "prev": "http://resour.ce/thingy/?offset=10&limit=10"
            "self": "http://resour.ce/thingy/?offset=20&limit=10"
            "next": "http://resour.ce/thingy/?offset=30&limit=10"
        },

        "items": [
            object,
            object,
            ...
        ],
    }



    Process

    Links
    Embed
    ##########################

    Request lifecycle

    Authenticate
    Throttle
    Cache

    parse_request
        parse_url
        parse_method
        parse_body
        parse_query

    Option
        before
        *{named}
        after

    Validate
    Hydrate
        before
        *{named}
        after

    redjango

    # EITHER
    One
    # OR
    Many
        filter
            before
            *{named}
            after
        slice
    # ALWAYS

    undjango

    Dehydrate
        before
        *{named}
        after

    Serialize
        **to_{format}

    ##########################

