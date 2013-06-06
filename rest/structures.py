import types
import optparse
import inspect

class StaticMeta:
    def __new__(meta, name, bases, attrs):
        for key, val in attrs.items():
            if (hasattr(val, '__call__') and
                    not isinstance(val, types.FunctionType)):
                attrs[key] = staticmethod(val)
        return type.__new__(meta, name, bases, attrs)

class NestedClass:
    pass

class NestingMeta(type):
    """
    This metaclass provides implicit inheritance for nested classes.

    Any subclass of NestedClass is added to a list by name so that descendants
    of the Nesting class extend them automatically.

    >>> class _1(metaclass=NestingMeta):
    ...     class A(NestedClass):
    ...         def __init__(self):
    ...             print('_1.A')
    ...     class B(NestedClass):
    ...         def __init__(self):
    ...             print('_1.B')
    ...     class C(NestedClass):
    ...         def __init__(self):
    ...             print('_1.C')
    ...
    >>> class _2(_1):
    ...     class A:
    ...         def __init__(self):
    ...            print('_2.A')
    ...     class B:
    ...         def __init__(self):
    ...            super().__init__()
    ...            print('_2.B')
    ...
    >>> class _3(_2):
    ...     class A:
    ...         def __init__(self):
    ...             super().__init__()
    ...             print('_3.A')
    ...     class B:
    ...         def __init__(self):
    ...             super().__init__()
    ...             print('_3.B')
    ...     class C:
    ...         def __init__(self):
    ...             super().__init__()
    ...             print('_3.C')
    ...
    >>> classes = [_1, _2, _3]
    >>> def run():
    ...    for c in map(lambda x: x(), classes):
    ...         print(c.__class__.__name__)
    ...         c.A()
    ...         c.B()
    ...         c.C()
    ...
    >>> run()
    _1
    _1.A
    _1.B
    _1.C
    _2
    _2.A
    _1.B
    _2.B
    _1.C
    _3
    _2.A
    _3.A
    _1.B
    _2.B
    _3.B
    _1.C
    _3.C
    """
    def __new__(meta, name, bases, attrs):
        # A list of classes that extend themselves with nametwins down the
        # hierarchy
        attrs['_nested_classes'] = []

        # A dictionary of tuples containing the nested classes of bases per
        base_nests = {}

        # Collect all nested classes from bases
        for base in bases:
            for key in getattr(base, '_nested_classes', []):
                val = getattr(base, key)
                if key in base_nests:
                    base_nests[key] += val,
                else:
                    base_nests[key] = val,

        # Process nests on the new class and update the list with their names
        for key, val in attrs.items():
            if key in base_nests:
                # Merge a nested classes with its supers
                attrs[key] = type(
                        key,
                        (val,) + base_nests.pop(key),
                        {})
                attrs['_nested_classes'].append(key)
            else:
                # Add all subclasses of NestedClass to the list
                try:
                    if issubclass(val, NestedClass):
                        attrs['_nested_classes'].append(key)
                except TypeError:
                    pass

        # Add all nests from bases not extended on the new class directly
        for key, val in base_nests.items():
            attrs[key] = type(key, val, {})
            attrs['_nested_classes'].append(key)

        return super().__new__(meta, name, bases, attrs)


class NestedApi(NestedClass):
    def _methods(self):
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if not name.startswith('_') and not name in ('before', 'after'):
                yield name, method

class Updater(NestedApi):
    """
    Takes a dictionary data object and updates all keys by their matching
    methods return values.

        def signature(self, data):
            return data['something'] * 100

    All keys in the `omits` tuple are removed from the dictionary
    """

    omits = ()

    def __call__(self, data=None):
        if isinstance(data, list):
            return [self(d) for d in data]

        if hasattr(self, 'before'):
            data = self.before(data)

        for name, method in self._methods():
            data[name] = method(data)

        if hasattr(self, 'after'):
            data = self.after(data)

        for key in self.omits:
            if key in data:
                del data[key]

        return data


class Reducer(NestedClass):
    """
    Heads up! Unspecified evaluation order, therefore operations must
    be commutative.

    Reduce on the queryset

    def signature(self, queryset, val):
        return queryset.filter(value__gt=val)
    """
    def __call__(self, queryset=None, **query):
        if hasattr(self, 'before'):
            queryset = self.before(queryset, **query)

        for key, val in query.items():
            method = getattr(self, key, None)
            if method:
                queryset = method(queryset, val)

        if hasattr(self, 'after'):
            queryset = self.after(queryset, **query)

        return queryset


class Mapper(NestedClass):
    """
    This class acts as a namespace for static functions which get called with
    arguments passed in a dictionary. With the following signature:

    def signature(self, resource, val):
        resource.value = val


    Heads up! Unspecified evaluation order, therefore operations must
    be commutative.
    """
    def __call__(self, resource, **options):
        if hasattr(self, 'before'):
            self.before(resource, **options)

        for key, val in options.items():
            method = getattr(self, key, None)
            if method:
                method(resource, val)

        if hasattr(self, 'after'):
            self.after(resource, **options)

def cache(name):
    attr = '_' + name.lower()
    @classmethod
    def call(cls, *a, **kw):
        if not hasattr(cls, attr):
            setattr(cls, attr, getattr(cls, name)())
        return getattr(cls, attr)(*a, **kw)
    return call


if __name__ == '__main__':
    import doctest
    doctest.testmod()
