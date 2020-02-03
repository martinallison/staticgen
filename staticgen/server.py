import livereload

from . import build
from .conf import conf


def serve():
    build.build()
    server = livereload.Server()
    server.watch(conf.base_path(), build.build)
    server.serve(port=8080, root=conf.build_path())
