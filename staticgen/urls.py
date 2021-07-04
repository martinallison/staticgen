from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Iterable, Mapping, Optional

if TYPE_CHECKING:
    from . import app, views


ForEach = Mapping[str, Callable[["app.App"], Iterable]]


@dataclass
class Url:
    name: str
    pattern: str
    view: views.View
    foreach: ForEach


def url(
    pattern: str, view: views.View, *, name: str, foreach: Optional[ForEach] = None
) -> Url:
    """
    Create a URL.

    URLs define where content should be accessible from in the resulting built site.

    A URL has a pattern that maps to a view. A view is callable that takes an `app.App`
    and returns some string content.

    The string content returned by a view is output to a file at the URL path relative
    to the build directory.

    Example:

        # views.py
        def hello(app):
            return "<body><p>Hello</p></body>"

        # urls.py
        urls = [url("/hello", view, name="hello")]

        # conf.py
        urlconf = "project.urls"

        staticgen serve --conf="path.to.conf"

        GET localhost/hello
        -> <body><p>Hello</p></body>
    """
    return Url(pattern=pattern, view=view, name=name, foreach=foreach or {})
