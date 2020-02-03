import os

import click

from distutils import dir_util as dirs

from . import site
from .conf import conf


tick = click.style('✓', fg='green', bold=True)


def iter_urls():
    for url in conf.urls:
        yield from url.flatten()


def write_content(url, content):
    url = url.strip('/')

    if '.' in url.split('/')[-1]:
        file_path = conf.build_path(url)
        directory, _ = os.path.split(file_path)
    else:
        directory = conf.build_path(url)
        file_path = os.path.join(directory, 'index.html')

    dirs.mkpath(directory)
    with open(file_path, 'w') as f:
        f.write(content)


def build():
    try:
        dirs.remove_tree(conf.build_path())
    except OSError:
        pass

    click.echo('Building routes')
    for url, view in iter_urls():
        write_content(url, view())
        click.echo(f'- {url} ' + tick)

    click.echo('Copying static')
    dirs.copy_tree(
        conf.base_path(conf.static_dir),
        conf.build_path(conf.static_dir),
    )
    click.echo(tick)

    click.echo('Copying root')
    dirs.copy_tree(
        conf.base_path(conf.root_dir),
        conf.build_path(),
    )
    click.echo(tick)

    click.echo('Done')
