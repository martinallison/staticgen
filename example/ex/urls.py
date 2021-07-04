from staticgen import urls, views


def home(request: views.Request) -> views.Response:
    t = request.app.template("home.html")
    return views.Response(content=t.render())


def article(request: views.Request, *, slug: str) -> views.Response:
    title = " ".join(slug.title().split("-"))
    return views.Response(
        content=f"<h1>{title}</h1><p>This is something about {title.lower()}"
    )


urls = [
    urls.url("/", home, name="home"),
    urls.url(
        "/{slug}", article, name="article", foreach={"slug": lambda app: ("thing",)}
    ),
]
