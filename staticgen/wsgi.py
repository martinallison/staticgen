from __future__ import annotations

import mimetypes
from pathlib import Path
from typing import TYPE_CHECKING, Dict, Iterable, List, Optional, Protocol, Tuple, Union

from . import http

if TYPE_CHECKING:
    from . import site


Environ = Dict[str, str]
HeaderItems = Iterable[Tuple[str, str]]

Headers = Dict[str, str]
Response = Tuple[str, Headers, Union[str, bytes]]


class StartResponse(Protocol):
    def __call__(self, status: str, header_items: HeaderItems) -> None:
        ...


class App(Protocol):
    def __call__(self, environ: Environ, start_response: StartResponse) -> List[bytes]:
        ...


def app(
    site_app: "site.App", environ: Environ, start_response: StartResponse
) -> List[bytes]:
    response: Optional[Response] = None

    path = environ["PATH_INFO"]
    method = environ["REQUEST_METHOD"]
    content_type = _content_type_for_path(path)

    if method != "GET":
        response = _method_not_allowed(method)

    for view in site_app.resolve_url(path):
        try:
            content = view().content
        except http.Http404:
            continue

        response = _ok(content, content_type=content_type)
        break

    return _response(start_response, response or _not_found(path))


def _response(start_response: StartResponse, response: Response) -> List[bytes]:
    status, headers, body = response
    start_response(status, _headers(headers))
    return [body.encode("utf-8") if isinstance(body, str) else body]


def _ok(content: Union[str, bytes], content_type: str) -> Response:
    return (
        "200 OK",
        {"Content-Type": content_type},
        content,
    )


def _not_found(path: str) -> Response:
    return (
        "404 Not Found",
        {"Content-Type": "text/plain"},
        f"Request path not found: {path}",
    )


def _method_not_allowed(method: str) -> Response:
    return (
        "405 Method Not Allowed",
        {"Content-Type": "text/plain"},
        f"Method not allowed: {method}",
    )


def _headers(d: Dict[str, str]) -> List[Tuple[str, str]]:
    return list(d.items())


def _content_type_for_path(path: str) -> str:
    return mimetypes.guess_type(path)[0] if Path(path).suffix else "text/html"
