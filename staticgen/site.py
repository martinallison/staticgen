import os
import urllib.parse as urlparse

import jinja2

from .conf import conf


def url_for(name, **params):
    pattern = conf.urls_by_name[name].pattern
    return pattern.format(**params)


def static_url_for(file_path):
    static_path = os.path.join(conf.static_dir, file_path)
    return urlparse.urljoin('/', static_path)


def get_jinja():
    templates = conf.base_path(conf.template_dir)
    loader = jinja2.FileSystemLoader([templates])
    jinja = jinja2.Environment(loader=loader)
    jinja.globals.update(
        url_for=url_for,
        static_url_for=static_url_for,
    )
    return jinja
