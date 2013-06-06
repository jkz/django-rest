from django.db.models.fields import Field

class NestedResource:
    def __init__(self, related_model):
        pass

class Status(Resource):
    model = models.Status

    user = fields.One(User, 'user')
    likes = fields.Many(Like, 'status')
    comments = fields.Many(Response, 'status')
    tags = fields.Many(Tag, 'status', values_list=True)

    template = {
        'fields': ['id', 'text', 'timestamp'],
        'related': {
            'user': {
                'resource': User,
            }
        }
    }

class One(NestedResource):
    def __init__(self, resource, relation, template=None, merge=False):
            values_list=False, flat=True):
        self.relation = relation
        self.resource = resource
        self.template = resource.template if template is None else template
        self.merge = merge
        self.values_list = values_list
        self.flat = flat

    def get_field(self):
        if hasattr(self.relation, 'db_column'):
            return self.relation.db_column
        else:
            return self.relation

    def __call__(self, instance):
        uid = getattr(instance, get_field())
        return self.resource(ids={'uid': uid})


class Many(NestedResource):
    def __init__(self, resource, relation, template=None, values_list=False,
            flat=True):
        self.relation = relation
        self.resource = resource
        self.template = resource.template if template is None else template
        self.values_list = values_list
        self.flat = flat

    def __call__(self, instance):
        rel = instance.pk.ids['uid']
        return self.resource(ids={'rel': rel})

