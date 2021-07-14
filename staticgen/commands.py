from typing import Optional

import click

from . import build as _build
from . import server, site


class App(click.ParamType):
    name = "conf"

    def convert(
        self, value: Optional[str], param: Optional[str], ctx: click.Context
    ) -> site.App:
        return site.from_module(value)


takes_app = click.option("-c", "--conf", "app", type=App())


@click.group()
def main():
    pass


@main.command()
@takes_app
def build(app: site.App):
    _build.build(app)


@main.command()
@takes_app
def serve(app: site.App):
    server.serve(app)


if __name__ == "__main__":
    main()
