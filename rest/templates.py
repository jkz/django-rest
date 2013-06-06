from .structures import NestedClass

class Template(NestedClass):
    '''
    fields = []
    exclude = []
    aliases = {}
    related = {}

    values_list = False
    flat = True
    merge = False
    prefix = ''

    allow_missing = False
    camelcase = False

     This can also be a dictionary to filter the data
    def prehook(self, objects):
        return objects

    def posthook(self, instance, attrs):
        return instance
    '''

    def __call__(self, **options):
        template = {}

        #TODO use default options from settings

        for key in ('fields', 'exclude', 'aliases', 'values_list', 'posthook',
                'flat', 'prefix', 'merge', 'allow_missing', 'camelcase',
                'prehook', 'related'):
            if key in options:
                template[key] = options[key]
            elif hasattr(self, key):
                template[key] = getattr(self, key)

        if 'related' in template:
            template['related'] = template['related'].copy()

            for key, val in template['related'].items():
                template['related'][key] = build_template(val)

        return template


def build_template(val, **options):
    if hasattr(val, 'template'):
        return build_template(val.template, **options)
    elif callable(val):
        return val(**options)
    elif hasattr(val, '__getitem__') and 'template' in val:
        return build_template(val, **options)
    elif hasattr(val, 'copy'):
        return val.copy()
    else:
        return val

