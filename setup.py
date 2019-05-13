from setuptools import setup, find_packages, Extension
import os
from sys import platform
import pybind11

REQUIRED_PACKAGES = [
    'protobuf >= 3.1.0',
    'grpcio >= 1.1.0',
    'toml >= 0.9.2',
    'enum34 >= 1.1.6',
    'numpy >= 1.12.0',
    'scipy >= 0.18.1',
    'storehouse >= 0.1.0'
]

package_data = {
    'scannerpy': [
        'build/*.so',
    ]
}

ROOT_DIR='.'

def get_build_dirs(d):
    return [t[0]+'/*.*' for t in os.walk('build/'+d) if 'CMakeFiles' not in t[0]]

package_data['scannerpy'] += get_build_dirs('scanner')
package_data['scannerpy'] += get_build_dirs('stdlib')
package_data['scannerpy'] += ['include/{}/*.h'.format(t[0])
                              for t in os.walk('scanner')]


# Borrowed from https://github.com/pytorch/pytorch/blob/master/setup.py
def make_relative_rpath(path):
    if platform == 'linux' or platform == 'linux2':
        return '-Wl,-rpath,$ORIGIN/' + path
    else:
        return '-Wl,-rpath,@loader_path/' + path


module1 = Extension(
    'scannerpy._python',
    include_dirs = [ROOT_DIR,
                    os.path.join(ROOT_DIR, 'build'),
                    os.path.join(ROOT_DIR, 'thirdparty', 'build', 'bin', 'storehouse', 'include'),
                    os.path.join(ROOT_DIR, 'thirdparty', 'build', 'bin', 'struck', 'include'),
                    pybind11.get_include(True),
                    ],
    libraries = ['scanner'],
    library_dirs = [ROOT_DIR,
                    os.path.join(ROOT_DIR, 'build'),
                    os.path.join(ROOT_DIR, 'thirdparty', 'build', 'bin', 'storehouse', 'lib'),
                    os.path.join(ROOT_DIR, 'thirdparty', 'build', 'bin', 'struck', 'lib'),
                    ],
    sources = [os.path.join(ROOT_DIR, 'scanner/engine/python.cpp')],
    extra_compile_args=['-std=c++11'],
)

setup(
    name='scannerpy',
    version='0.1.13',
    description='Efficient video analysis at scale',
    long_description='',
    url='https://github.com/scanner-research/scanner',
    author='Alex Poms and Will Crichton',
    author_email='wcrichto@cs.stanford.edu',

    package_dir={'': 'python'},
    packages=find_packages(where='python'),
    install_requires=REQUIRED_PACKAGES,
    package_data=package_data,

    license='Apache 2.0',
    keywords='video distributed gpu',
    ext_modules=[module1]
)
