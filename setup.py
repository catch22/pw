from setuptools import setup
import ast, re
from os.path import join, dirname, abspath


# determine __version__ from pw.py source (from mitsuhiko)
VERSION_RE = re.compile(r'__version__\s+=\s+(.*)')

with open('pw/__init__.py', 'rb') as fp:
  version_code = VERSION_RE.search(fp.read().decode('utf-8')).group(1)
  version = str(ast.literal_eval(version_code))


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
  long_description=open(join(dirname(abspath(__file__)), 'README')).read(),
  install_requires=['PyYAML', 'xerox', 'click>=2.0'],
  extras_require={'color': ['colorama']}
)
