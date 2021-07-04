from dataclasses import dataclass
from distutils import dir_util as dirs
from pathlib import Path

import click

from . import app

tick = click.style("✓", fg="green", bold=True)


@dataclass(frozen=True)
class Output:
    path: Path
    content: str


def build(app: app.App) -> None:
    try:
        dirs.remove_tree(str(app.build_dir))
    except OSError:
        pass

    click.echo("Rendering views")
    _render_views(app)
    click.echo(tick)

    click.echo("Copying root")
    dirs.copy_tree(str(app.root_dir), str(app.build_dir))
    click.echo(tick)

    click.echo("Done")


def _render_views(app: app.App) -> None:
    for url in app.generate_routes():
        path = _output_path(app.build_dir, url.url)
        response = url.view()

        dirs.mkpath(str(path.parent))

        with open(path, "w") as f:
            f.write(response.content)


def _output_path(build_dir: Path, path: str) -> Path:
    path = Path(path.strip("/"))

    output_path = build_dir / path
    if not path.suffix:
        output_path = output_path / "index.html"

    return output_path
