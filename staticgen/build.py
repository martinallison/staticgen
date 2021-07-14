from distutils import dir_util as dirs
from pathlib import Path

import click

from . import site

tick = click.style("✓", fg="green", bold=True)


def build(app: site.App) -> None:
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


def _render_views(app: site.App) -> None:
    for resolved in app.flatten_urls():
        path = app.build_dir / _output_path(resolved.url)
        response = resolved.view()

        dirs.mkpath(str(path.parent))

        with open(path, "w") as f:
            f.write(response.content)


def _output_path(path: str) -> Path:
    output_path = Path(path.strip("/"))
    return output_path if output_path.suffix else output_path / "index.html"
