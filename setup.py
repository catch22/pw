from distutils.core import setup

setup(
  name = 'pw',
  version = '0.1',
  description = 'Grep GPG-encrypted YAML password safe.',
  author = 'Michael Walter',
  author_email = 'michael.walter@gmail.com',
  url = 'https://github.com/catch22/pw',
  scripts = ['scripts/pw'],
  classifiers = [
    'Programming Language :: Python',
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'License :: OSI Approved :: MIT License',
  ],
  long_description = open('README.rst').read(),
  requires=['pyyaml', 'xerox'],
)
