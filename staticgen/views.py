from typing import List

from staticgen import http

from . import urls


def static(dir: str) -> urls.View:
    def view(request: http.Request, *, path: str) -> http.Response:
        try:
            with open(request.app.base_dir / dir / path.lstrip("/"), "rb") as f:
                content = f.read()
        except OSError:
            raise http.Http404()

        return http.Response(content=content)

    return view


# Not possible because it needs the app in scope
def static_urls(dir: str) -> List[urls.Url]:
    pass
