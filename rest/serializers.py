import json

from django.http import HttpResponse

class Serializer:
    def json(self, data):
        return json.dumps(data)

    def __call__(self, data, format):
        serializer = getattr(self, format)
        if serializer:
            content = serializer(data)
        else:
            content = ''
        return HttpResponse(content)
