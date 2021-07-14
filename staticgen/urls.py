from __future__ import annotations

from dataclasses import dataclass
from functools import partial
from typing import Callable, Mapping, Optional

import parse

from . import http

Kwargs = Mapping[str, str]

View = Callable[..., http.Response]
PartialView = Callable[[http.Request], http.Response]


@dataclass
class Match:
    kwargs: Kwargs


@dataclass
class Resolved:
    url: str
    view: PartialView


@dataclass
class Url:
    pattern: str
    view: View
    name: Optional[str]

    def format(self: Url, **kwargs: str) -> str:
        return self.pattern.format(**kwargs)

    def match(self: Url, path: str) -> Optional[Match]:
        if match := parse.parse(self.pattern, path):
            return Match(kwargs=match.named)
        return None

    def resolve(self: Url, kwargs: Mapping[str, str]) -> Resolved:
        path = self.format(**kwargs)
        view = partial(self.view, **kwargs)
        return Resolved(url=path, view=view)


def url(pattern: str, view: View, *, name: Optional[str] = None) -> Url:
    return Url(pattern=pattern, view=view, name=name)
