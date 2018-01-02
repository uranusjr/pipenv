import operator
import os
import winreg

from pip._vendor.packaging.version import parse as parse_version
from pipenv.utils import python_version

from .base import match_version


PYTHON_KEY_PATHS = [
    (winreg.HKEY_CURRENT_USER, 'Software', True),
    (winreg.HKEY_LOCAL_MACHINE, 'Software', True),
    (winreg.HKEY_LOCAL_MACHINE, 'Software\\Wow6432Node', False),
]


def guess_exe_location(install_path_key):
    """Make our best guess where the Python executable is.

    Recent CPython versions conforming to PEP 514 write an ``ExecutablePath``
    value to registry that we can simply use. Earlier versions only provide
    the installation root; in this case we append ``python.exe`` and hope it's
    good enough. It should be.
    """
    try:
        value, _ = winreg.QueryValueEx(install_path_key, 'ExecutablePath')
    except FileNotFoundError:
        install_path, _ = winreg.QueryValueEx(install_path_key, '')
        value = os.path.join(install_path, 'python.exe')
    return value


def iter_match(version):
    for priority, (root, prefix, not_cross) in enumerate(PYTHON_KEY_PATHS):
        try:
            key = winreg.OpenKey(root, '{}\\Python\\PythonCore'.format(prefix))
        except FileNotFoundError:
            continue
        subkey_count, _, _ = winreg.QueryInfoKey(key)
        for i in range(subkey_count):
            tag = winreg.EnumKey(key, i)
            if tag.endswith('-32'):
                not_cross = False
            try:
                subkey = winreg.OpenKey(key, '{0}\\InstallPath'.format(tag))
            except FileNotFoundError:
                continue
            full_path = guess_exe_location(subkey)
            exe_ver_s = python_version(full_path)
            if not exe_ver_s:
                continue
            exe_version = parse_version(exe_ver_s)
            if match_version(version, exe_version):
                # Used for sorting. If multiple installations of a version are
                # present, per-user is preferred to machine-wide. not_cross
                # puts the 64-bit version on top of 32-bit.
                sort_key = (
                    exe_version,
                    not_cross,
                    len(PYTHON_KEY_PATHS) - priority,
                )
                yield full_path, sort_key


def find_python(version):
    try:
        best, _ = max(iter_match(version), key=operator.itemgetter(1))
    except ValueError:
        pass
    else:
        return best
