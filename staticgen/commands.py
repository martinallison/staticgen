from typing import Optional

import click

from . import app
from . import build as _build
from . import server


class App(click.ParamType):
    name = "conf"

    def convert(
        self, value: Optional[str], param: Optional[str], ctx: click.Context
    ) -> app.App:
        return app.from_module(value)


takes_app = click.option("-c", "--conf", "app", type=App())


@click.group()
def main():
    pass


@main.command()
@takes_app
def build(app: app.App):
    _build.build(app)


@main.command()
@takes_app
@click.option("-s", "--strict", is_flag=True)
def serve(app: app.App, strict: bool):
    server.serve(app, strict=strict)


if __name__ == "__main__":
    main()
