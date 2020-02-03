import livereload

from . import build
from .conf import conf


def serve():
    server = livereload.Server()

    server.watch(conf.base_path(conf.templates), build.build)
    server.watch(conf.base_path(conf.root), build.build)
    server.watch(conf.base_path(conf.static), build.build)

    server.serve(port=8080, root=conf.build_path())
