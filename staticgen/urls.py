import collections
import functools
import itertools

import parse

from .conf import conf


BaseUrl = collections.namedtuple('Route', 'pattern, fn, name, generators')


class Url(BaseUrl):

    def generate_kwargs(self, fields):
        values = [self.generators[field]() for field in fields]
        for value_combination in itertools.product(*values):
            yield dict(zip(fields, value_combination))

    def flatten(self):
        pattern = self.pattern
        fn = self.fn
        parser = parse.Parser(pattern)
        fields = parser._named_fields or []

        if not fields:
            yield pattern, fn
        else:
            for field in fields:
                if field not in self.generators:
                    raise ValueError(f'{field} missing from generators')

            for kwargs in self.generate_kwargs(fields):
                yield pattern.format(**kwargs), functools.partial(fn, **kwargs)


def url(pattern, fn, *, name, generators=None):
    return Url(pattern, fn, name, generators or {})
