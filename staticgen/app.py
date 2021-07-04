from __future__ import annotations

import functools
import importlib
from dataclasses import dataclass
from functools import cached_property
from itertools import product
from pathlib import Path
from typing import Callable, Dict, Generator, List, Optional

import jinja2
import parse

from . import urls as _urls
from . import views, wsgi


@dataclass(frozen=True)
class Route:
    url: str
    view: Callable[[], views.Response]


@dataclass(frozen=True)
class App:
    """
    A static web application.

    This class holds everything required to build an application out of some
    configuration.
    """

    urls: List[_urls.Url]

    base_dir: Path
    build_dir: Path

    root_dir: Path
    template_dir: Path

    @cached_property
    def urls_by_name(self) -> Dict[str, _urls.Url]:
        return {url.name: url for url in self.urls}

    @cached_property
    def jinja(self) -> jinja2.Environment:
        loader = jinja2.FileSystemLoader([self.template_dir])
        env = jinja2.Environment(loader=loader)
        env.globals.update(url=self.url_for)
        return env

    def url_for(self, name: str, **params: Dict[str, str]) -> _urls.Url:
        return self.urls_by_name[name].pattern.format(**params)

    def template(self, name: str) -> jinja2.Template:
        return self.jinja.get_template(name)

    def resolve_url(
        self, url: str, strict: bool = False
    ) -> Optional[Callable[[], views.Response]]:
        app_url: Optional[_urls.Url] = None
        kwargs: Dict[str, str] = {}
        request = views.Request(app=self)

        if strict:
            app_url = next(
                (item for item in self.generate_routes() if url == item.url), None
            )
        else:
            for candidate_url in self.urls:
                if match := parse.parse(app_url.pattern, url):
                    app_url = candidate_url
                    kwargs = match.named
                    break

        if not app_url:
            return

        return functools.partial(app_url.view, request=request, **kwargs)

    def generate_routes(self) -> Generator[Route, None, None]:
        for url in self.urls:
            yield from _generate_routes_from_url(self, url)

    def wsgi(self, strict: bool) -> wsgi.Application:
        return functools.partial(wsgi.application, self, strict=strict)


def from_module(module_path: str) -> App:
    """
    Instantiate an app from a Python module with some configuration variables.
    """
    conf = importlib.import_module(module_path)
    urls = importlib.import_module(conf.urlconf)

    base_dir = Path(conf.__file__).absolute().parent

    return App(
        urls=urls.urls,
        base_dir=base_dir,
        build_dir=base_dir / conf.build_dir,
        root_dir=base_dir / conf.root_dir,
        template_dir=base_dir / conf.template_dir,
    )


def _generate_routes_from_url(app: App, url: _urls.Url) -> Generator[Route, None, None]:
    """
    Yield a route for each combination of values in a URL's `foreach` dict.

    Example:

        >>> def view(request, slug):
        ...    return f"<p>{slug}</p>"
        >>> slugs = ["thing", "hello"]
        >>> url = Url("/{slug}", view, name="slug-view", foreach={"slug": slugs})
        >>> list(_generated_routes_for_url(app, url))
        [
            Route("/thing", <partial view, args=(request, slug="thing")>),
            Route("/hello", <partial view, args=(request, slug="hello")>),
        ]
    """
    request = views.Request(app=app)
    parser = parse.Parser(url.pattern)
    fields = parser._named_fields or []

    if missing_fields := [field for field in fields if field not in url.foreach]:
        raise ValueError(
            f"URL {url.pattern} has fields {missing_fields!r} missing from `foreach`"
        )

    kwargs_list = _kwargs_for_url(app, url) if url.foreach else [{}]

    for kwargs in kwargs_list:
        view = functools.partial(url.view, request=request, **kwargs)
        formatted_url = url.pattern.format(**kwargs)
        yield Route(url=formatted_url, view=view)


def _kwargs_for_url(app: App, url: _urls.Url) -> Generator[Dict, None, None]:
    values = [generator(app) for generator in url.foreach.values()]

    for value_combination in product(*values):
        yield dict(zip(list(url.foreach), value_combination))
