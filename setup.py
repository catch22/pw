from setuptools import setup
from os.path import join, dirname, abspath

setup(
  name = 'pw',
  version = '0.2.2',
  description = 'Grep GPG-encrypted YAML password safe.',
  author = 'Michael Walter',
  author_email = 'michael.walter@gmail.com',
  url = 'https://github.com/catch22/pw',
  py_modules = ['pw'],
  entry_points = {
    'console_scripts': ['pw = pw:main']
  },
  classifiers = [
    'Programming Language :: Python',
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'License :: OSI Approved :: MIT License',
  ],
  long_description = open(join(dirname(abspath(__file__)), 'README.txt')).read(),
  install_requires=['PyYAML', 'xerox', 'termcolor'],
)
