# -*- coding: utf-8 -*-

import os

import click
import crayons

from pip._vendor.packaging.version import parse as parse_version, Version
from pipenv.environments import (
    PYENV_INSTALLED, SESSION_IS_INTERACTIVE,
    PIPENV_DONT_USE_PYENV, PIPENV_YES,
)

from . import pathname


class PythonInstallationNotFoundError(Exception):
    """Raised when a Python installation is not found on the current system.
    """


def iter_finders():
    if os.name == 'nt':
        from . import pep514
        yield pep514
    if PYENV_INSTALLED:
        from . import pyenv
        yield pyenv
    yield pathname


def confirm_install(prompt):
    if PIPENV_YES:
        return True
    return click.confirm(prompt, default=True)


def find_python(name, try_to_install=True):
    version = parse_version(name)
    if not isinstance(version, Version):    # Only support X[.Y[.Z]] schemes.
        raise PythonInstallationNotFoundError(name)
    for finder in iter_finders():
        python = finder.find_python(version)
        if python:
            return python

    if name is None or PIPENV_DONT_USE_PYENV or not SESSION_IS_INTERACTIVE:
        raise PythonInstallationNotFoundError(name)

    # We need to install Python.
    click.echo(
        u'{0}: Python {1} {2}'.format(
            crayons.red('Warning', bold=True),
            crayons.blue(name),
            u'was not found on your system…',
        ), err=True
    )
    for finder in iter_finders():
        try:
            install = finder.install_python
        except AttributeError:
            continue
        if not install(name, user_confirm=confirm_install):
            continue
        # Try again if the installation works.
        try:
            return find_python(name, try_to_install=False)
        except PythonInstallationNotFoundError:
            click.echo(
                '{0}: The Python you just installed cannot be located.'.format(
                    crayons.red('Warning', bold=True),
                ), err=True,
            )
            raise

    raise PythonInstallationNotFoundError(name)
