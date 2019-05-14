from __future__ import absolute_import, division, print_function, unicode_literals
from future import standard_library
standard_library.install_aliases()
import os
import urllib.request, urllib.error, urllib.parse
import errno

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def temp_directory():
    path = os.path.expanduser('~/.scanner/resources')
    mkdir_p(path)
    return path


def download_temp_file(url, local_path=None):
    if local_path is None:
        local_path = url.rsplit('/', 1)[-1]
    local_path = os.path.join(temp_directory(), local_path)
    mkdir_p(os.path.dirname(local_path))
    if not os.path.isfile(local_path):
        print('Downloading {:s} to {:s}...'.format(url, local_path))
        f = urllib.request.urlopen(url)
        with open(local_path, 'wb') as local_f:
            local_f.write(f.read())
    return local_path

