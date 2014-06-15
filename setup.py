from setuptools import setup
import ast, io, re
from os.path import join, dirname, abspath


# determine __version__ from pw.py source (adapted from mitsuhiko)
VERSION_RE = re.compile(r'__version__\s+=\s+(.*)')

with io.open('pw/__init__.py', encoding='utf-8') as fp:
  version_code = VERSION_RE.search(fp.read()).group(1)
  version = str(ast.literal_eval(version_code))


# read long description and convert to RST
long_description = io.open(join(dirname(abspath(__file__)), 'README.md'), encoding='utf-8').read()
try:
  import pypandoc
  long_description = pypandoc.convert(long_description, 'rst', format='md')
except ImportError:
  pass


# package metadata
setup(
  name='pw',
  version=version,
  description='Grep GPG-encrypted YAML password safe.',
  author='Michael Walter',
  author_email='michael.walter@gmail.com',
  url='https://github.com/catch22/pw',
  packages = ['pw'],
  entry_points={
    'console_scripts': ['pw = pw.cli:pw']
  },
  classifiers=[
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 3',
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'License :: OSI Approved :: MIT License',
  ],
  long_description=long_description,
  install_requires=['PyYAML', 'xerox', 'python-gnupg', 'click>=2.0'],
  extras_require={'color': ['colorama']},
  tests_require = ['pytest'],
)
