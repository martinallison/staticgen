import click

from . import build as _build, server
from .conf import conf


@click.group()
@click.argument('dir')
def main(dir):
    conf.load_from_dir(dir)


@main.command()
def build():
    _build.build()


@main.command()
def serve():
    server.serve()


if __name__ == '__main__':
    main()
