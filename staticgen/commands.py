import click

from . import build as _build, server
from .conf import conf


@click.group()
@click.argument('conf_module')
def main(conf_module):
    conf(conf_module)


@main.command()
def build():
    _build.build()


@main.command()
def serve():
    server.serve()


if __name__ == '__main__':
    main()
