from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property, partial
from importlib import import_module
from pathlib import Path
from typing import Dict, Generator, List

import jinja2

from . import http, urls, wsgi


@dataclass
class App:
    urls: List[urls.Url]

    base_dir: Path
    build_dir: Path

    template_dir: Path

    @cached_property
    def urls_by_name(self) -> Dict[str, urls.Url]:
        return {url.name: url for url in self.urls if url.name is not None}

    @cached_property
    def jinja(self) -> jinja2.Environment:
        loader = jinja2.FileSystemLoader([self.template_dir])
        env = jinja2.Environment(loader=loader)
        env.globals.update(url=self.url_for)
        return env

    def url_for(self, name: str, **params: Dict[str, str]) -> str:
        return self.urls_by_name[name].format(**params)

    def template(self, name: str) -> jinja2.Template:
        return self.jinja.get_template(name)

    def resolve_url(self, path: str) -> List[urls.PartialView]:
        request = http.Request(app=self, url=path)

        def _generate_views() -> Generator[urls.PartialView, None, None]:
            for url in self.urls:
                if match := url.match(path):
                    yield partial(url.view, request, **match.kwargs)

        return list(_generate_views())

    def wsgi(self) -> wsgi.App:
        return partial(wsgi.app, self)


def from_module(module_path: str) -> App:
    conf = import_module(module_path)
    urls = import_module(conf.urlconf)  # type: ignore

    base_dir = Path(conf.__file__).absolute().parent

    return App(
        urls=urls.urls,  # type: ignore
        base_dir=base_dir,
        build_dir=base_dir / conf.build_dir,  # type: ignore
        template_dir=base_dir / conf.template_dir,  # type: ignore
    )
