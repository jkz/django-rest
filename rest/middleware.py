import math

from django.utils import timezone
from django.core.cache import cache
from django.http import HttpResponse

from . import models
from . import exceptions

# Authentication
class AuthenticationMiddelware:
    def process_view(self, request, view_func, view_args, view_kwargs):
        # Skip if we're not dealing with a resource
        if not isinstance(view_func, Resource):
            return

        # Check if resource requires authenticated user
        try:
            if view_func.login_required and not request.user.is_authenticated():
                raise exceptions.Unauthorized
        except AttributeError:
            pass

        # Call custom is_unauthorized on resource if present
        try:
            if view_func.is_unauthorized():
                raise exceptions.Unauthorized
        except AttributeError:
            pass

    def process_exception(self, request, exception):
        if isinstance(exception, exceptions.Unauthorized):
            return HttpResponse(exception.msg, status=403)


# Throttle
class Throttle:
    """
    Throttler is the Keeper of the Bandwith.
    He manages rate limits of users. And replenishes shares of those
    in fixed intervals.
    """
    # in seconds
    interval = 60 * 60

    # decrement per call
    cost = 1

    # maximum points
    pool = 300

    # number of points replenished per interval
    gain = 300

    def replenish_amount(self, delta):
        return delta * self.gain // self.interval

    def full_replenish_time(self, value):
        return math.ceil((self.pool - value) / self.gain) * interval

    class Pool:
        STAMP_SUFFIX = '__throttle_stamp'
        VALUE_SUFFIX = '__throttle_value'

        def __init__(self, request, throttle):
            self.throttle = throttle
            self.request = request

            self.value = self.get_value(request, throttle)

            self.init(request, throttle)

        def __add__(self, other):
            if not isinstance(other, int):
                raise TypeError
            stamp = timezone.now()
            delta = stamp - self.timestamp
            gain = self.throttle.replenish_amount(delta)
            value = self.value + gain
            new = value + other
            if new < 0:
                self.set_value(value, stamp)
                raise exceptions.ThrottleException()

            self.set_value(new, stamp)
            return self

        def __iadd__(self, other):
            return self + other

        def __sub__(self, other):
            return self + -other

        def __isub__(self, other):
            return self + -other

        def init(self):
            self.cache = cache

        def get_key(self, request):
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[-1].strip()
            else:
                ip = request.META.get('REMOTE_ADDR')
            return ip

        def _get(self, request):

        def get_timestamp(self, request, throttle):
            return self.cache.get(cls.get_key(request) + STAMP_SUFFIX, throttle.pool)

        def get_value(self, request, throttle):
            return self.cache.get(cls.get_key(request) + VALUE_SUFFIX, throttle.pool)

        def _set(self, request, value, stamp):
            expire = self.throttle.full_replenish_time(value)
            stamp = stamp or timezone.now()
            self.set_value(key, value, expire)
            self.set_timestamp(key, stamp, expire)

        def set_value(self, key, value, expire=None):
            self.cache.set(key + VALUE_SUFFIX, value, expire)

        def set_timestamp(self, key, stamp, expire):
            self.cache.set(key + STAMP_SUFFIX, stamp, expire)



    def get_current(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def replenish(self, prev, current, timestamp)
        return


    def __call__(self, request):
        pool = self.pool(request, self)




# Permissions
class PermissionsMiddleware:
    pass


