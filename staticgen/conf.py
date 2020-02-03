from functools import cached_property as cached_prop
import importlib
import importlib.util
import os
import sys


def normjoin(*args):
    return os.path.normpath(os.path.join(*args))


def load_from_file(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Conf:

    def __init__(self):
        self._loaded = False
        self._base_path = None

    def load_from_dir(self, dir_path):
        if self._loaded:
            raise ValueError("Already configured conf")

        self._base_path = os.path.abspath(dir_path)
        conf = load_from_file('conf', self.base_path('conf.py'))
        self.load(conf)

    def load(self, module):
        attrs = {attr: getattr(module, attr) for attr in dir(module)}

        for attr, value in attrs.items():
            if not attr.startswith('_'):
                setattr(self, attr, value)

        self._loaded = True

    def base_path(self, *paths):
        return normjoin(self._base_path, *paths)

    def build_path(self, *paths):
        return self.base_path(self.build, *paths)

    @cached_prop
    def urls(self):
        if remove_path := self._base_path not in sys.path:
            sys.path.append(self._base_path)

        urls = importlib.import_module(self.urlconf).urls

        if remove_path:
            sys.path.remove(self._base_path)

        return urls

    @cached_prop
    def urls_by_name(self):
        return {url.name: url for url in self.urls}


conf = Conf()
