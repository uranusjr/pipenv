import os

import click
import crayons

from pip._vendor.packaging.version import parse as parse_version
from pipenv.environments import PYENV_ROOT

from .base import match_version


def find_python(version):
    versions_dir = os.path.join(PYENV_ROOT, 'versions')
    if os.path.isdir(versions_dir):
        versions = (
            v for v in (parse_version(n) for n in os.listdir(versions_dir))
            if match_version(version, v)
        )
    else:
        click.echo(
            '{0}: PYENV_ROOT is not set. New Python paths will '
            'probably not be exported properly after installation.'
            ''.format(crayons.red('Warning', bold=True)),
            err=True,
        )
        versions = []
    try:
        best = max(versions)
    except ValueError:
        pass
    else:
        return os.path.join(versions_dir, best.base_version, 'bin', 'python')
