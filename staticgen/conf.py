import functools
import importlib
import os


def normjoin(*args):
    return os.path.normpath(os.path.join(*args))


class Conf:

    def __init__(self):
        self._loaded = False
        self._module = None
        self._base_path = None

    def __call__(self, module):
        if self._loaded:
            raise ValueError("Already configured conf")
        self._module = module
        self.load()

    @functools.cached_property
    def urls(self):
        return importlib.import_module(self.url_module).urls

    @functools.cached_property
    def urls_by_name(self):
        return {url.name: url for url in self.urls}

    def build_path(self, *paths):
        return self.base_path(self.build, *paths)

    def base_path(self, *paths):
        return normjoin(self._base_path, *paths)

    def load(self):
        conf = importlib.import_module(self._module)
        self._base_path = os.path.dirname(conf.__file__)

        attrs = {attr: getattr(conf, attr) for attr in dir(conf)}
        for attr, value in attrs.items():
            if not attr.startswith('_'):
                setattr(self, attr, value)

        self._loaded = True


conf = Conf()
