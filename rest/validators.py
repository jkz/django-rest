from .structures import NestedClass

class Validator(NestedClass):
    """
    When called with a dictionary, the validator runs all methods
    matching its keys with their values as parameter. When a method
    returns a string, it is added to a dictionary of error messages.

    The special cases before and after are called at their respective
    times and should return a sequence of or yield (key, value) pairs.

    Data is considered valid if the validator call returns the empty
    dictionary.
    """
    def __call__(self, **data):
        messages = {}

        if hasattr(self, 'before'):
            for key, val in self.before(data):
                messages[key] = val

        for key, val in data.items():
            validator = getattr(self, key, None)
            if validator:
                m = validator(val)
                if m:
                    messages[key] = m

        if hasattr(self, 'after'):
            for key, val in self.after(data):
                messages[key] = val

        return messages

