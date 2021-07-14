import livereload

from . import site


def serve(app: site.App):
    server = livereload.Server(app.wsgi())
    server.watch(app.base_dir)
    server.serve(port=8080, root=app.build_dir)
