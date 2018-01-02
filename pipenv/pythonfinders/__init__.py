import os

from pip._vendor.packaging.version import parse as parse_version, Version
from pipenv.environments import PYENV_INSTALLED

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


def find_python(name):
    version = parse_version(name)
    if not isinstance(version, Version):    # Only support X[.Y[.Z]] schemes.
        raise PythonInstallationNotFoundError(name)
    for finder in iter_finders():
        python = finder.find_python(name)
        if python:
            return python
    raise PythonInstallationNotFoundError(name)
