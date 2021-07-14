from staticgen import http
from staticgen import urls as app_urls
from staticgen import views


def home(request: http.Request) -> http.Response:
    t = request.app.template("home.html")
    return http.Response(content=t.render())


def article(request: http.Request, *, slug: str) -> http.Response:
    if slug not in ("thing", "stuff"):
        raise http.Http404()

    title = " ".join(slug.title().split("-"))
    return http.Response(
        content=f"<h1>{title}</h1><p>This is something about {title.lower()}"
    )


urls = [
    app_urls.url("/", home, name="home"),
    app_urls.url("/{slug}", article, name="article"),
    app_urls.url("/favicon.ico", views.static(dir="root"), name="static"),
]
