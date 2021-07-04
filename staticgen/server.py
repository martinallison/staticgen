import livereload

from . import app


def serve(app: app.App, strict: bool):
    server = livereload.Server(app.wsgi(strict=strict))
    server.watch(app.base_dir)
    server.serve(port=8080, root=app.build_dir)
