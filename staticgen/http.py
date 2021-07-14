from dataclasses import dataclass
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from . import site


class Http404(Exception):
    pass


@dataclass(frozen=True)
class Request:
    app: "site.App"
    url: str


@dataclass(frozen=True)
class Response:
    content: Union[str, bytes]
