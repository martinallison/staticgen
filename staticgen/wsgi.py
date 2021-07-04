from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Dict, Iterable, List, Protocol, Tuple

if TYPE_CHECKING:
    from . import app


Environ = Dict[str, str]
HeaderItems = Iterable[Tuple[str, str]]

Headers = Dict[str, str]
Response = Tuple[str, Headers, str]


class StartResponse(Protocol):
    def __call__(self, status: str, header_items: HeaderItems) -> None:
        ...


class Application(Protocol):
    def __call__(self, environ: Environ, start_response: StartResponse) -> List[bytes]:
        ...


class View(Protocol):
    def __call__(self, environ: Environ) -> Response:
        ...


def application(
    app: "app.App",
    environ: Environ,
    start_response: StartResponse,
    *,
    strict: bool = False,
) -> List[bytes]:
    """
    Return some bytes in response to a WSGI request based on urls defined in `app`.

    Only GET requests are allowed to emulate a static server. Generally anything that
    can't be constructed/achieved at build time is not implemented.

    Args:

        * app: The staticgen app with URL definitions
        * environ, start_response: WSGI arguments passed by the server
        * strict: Whether or not to 404 for URLs that wouldn't appear in the built site
    """

    if environ["REQUEST_METHOD"] != "GET":
        return _response(environ, start_response, _method_not_allowed)

    path = environ["PATH_INFO"]
    if not (view := app.resolve_url(path, strict=strict)):
        return _response(environ, start_response, _not_found)

    def wsgi_view(environ: Environ) -> Response:
        response = view()
        return (
            "200 OK",
            {"Content-Type": _content_type_for_path(path)},
            response.content,
        )

    return _response(environ, start_response, wsgi_view)


def _response(
    environ: Environ, start_response: StartResponse, view: View
) -> List[bytes]:
    status, headers, body = view(environ)
    start_response(status, _headers(headers))
    return [body.encode("utf-8")]


def _not_found(environ: Environ) -> Response:
    path = environ["PATH_INFO"]
    return (
        "404 Not Found",
        {"Content-Type": "text/plain"},
        f"Request path not found: {path}",
    )


def _method_not_allowed(environ: Environ) -> Response:
    method = environ["REQUEST_METHOD"]
    return (
        "405 Method Not Allowed",
        {"Content-Type": "text/plain"},
        f"Method not allowed: {method}",
    )


def _headers(d: Dict[str, str]) -> List[Tuple[str, str]]:
    return list(d.items())


def _content_type_for_path(path: str) -> str:
    return {
        "": "text/html",
        ".txt": "text/plain",
        ".html": "text/html",
        ".js": "text/javascript",
        ".json": "application/json",
    }[Path(path).suffix]
