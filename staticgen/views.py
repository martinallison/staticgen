from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol


@dataclass(frozen=True)
class Request:
    app: "app.App"


@dataclass(frozen=True)
class Response:
    content: str


class View(Protocol):
    def __call__(self, request: Request, *args, **kwargs) -> Response:
        ...
