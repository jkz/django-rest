import www

from .structures import NestedClass

DEFAULT_LIMIT = 10

class Slicer(NestedClass):
    """A offset/limit slicer"""
    offset = 0
    limit = DEFAULT_LIMIT

    max_limit = None
    max_offset = None

    limit_name = 'limit'
    offset_name = 'offset'
    count_name = 'count'

    next_name = 'next'
    prev_name = 'prev'

    def get_limit(self, resource):
        return resource.query.get(self.limit_name, None)

    def validate_limit(self, limit):
        if limit is not None:
            try:
                limit = int(limit)
            except ValueError:
                raise Exception("Please provide a valid integer value")
            if limit < 0:
                raise Exception("Please provide a valid positive integer value")
        if self.max_limit is not None:
            limit = min(max(limit, 0), max_limit)
        return limit

    def get_offset(self, resource):
        return resource.query.get(self.offset_name, 0)

    def validate_offset(self, offset):
        if offset is not None:
            try:
                offset = int(offset)
            except ValueError:
                raise Exception("Please provide a valid integer value")
            if offset < 0:
                raise Exception("Please provide a valid positive integer value")
        if self.max_offset is not None:
            offset = min(max(offset, 0), max_offset)
        return offset

    def get_count(self, collection):
        try:
            return collection.count()
        except (AttributeError, TypeError):
            # Fallback to len if not QuerySet
            return len(collection)

    def get_uri(self, resource, limit, offset):
        query = {self.limit_name: limit, self.offset_name: offset}
        return www.URL(resource.location(), **query)

    def get_prev(self, resource, limit, offset):
        if limit is None or offset - limit < 0:
            return None
        return self.get_uri(resource, limit, offset - limit)

    def get_next(self, resource, limit, offset, count):
        if limit is None or offset + limit >= count:
            return None
        return self.get_uri(resource, limit, offset + limit)

    def get_slice(self, collection, limit=None, offset=None):
        offset = offset or 0
        if limit is None:
            return collection[offset:]
        else:
            return collection[offset:offset + limit]

    def __call__(self, resource, collection):
        limit = self.validate_limit(self.get_limit(resource))
        offset = self.validate_offset(self.get_offset(resource))
        count = self.get_count(collection)

        slice = self.get_slice(collection, limit, offset)

        meta = {
            self.count_name: count,
        }

        if offset:
            meta[self.offset_name] = offset

        if limit:
            meta[self.limit_name] = limit

        prev = self.get_prev(resource, limit, offset)
        if prev:
            meta[self.prev_name] = prev

        next = self.get_next(resource, limit, offset, count)
        if next:
            meta[self.next_name] = next

        return slice, meta


class Paginator:
    offset_name = 'page'
    limit_name = 'size'

    #TODO:
    # 0 and 1 indexed paging methods
