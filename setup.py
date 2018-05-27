from __future__ import absolute_import, division, print_function
from setuptools import setup
import ast, io, re, sys, os

# determine version (adapted from mitsuhiko)
VERSION_RE = re.compile(r"__version__\s+=\s+(.*)")
with io.open("pw/__init__.py", encoding="utf-8") as fp:
    version_code = VERSION_RE.search(fp.read()).group(1)
    version = str(ast.literal_eval(version_code))

# read long description
long_description = io.open(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
    encoding="utf-8",
).read()


# collect installation requirements
install_requires = ["click>=5.1", "colorama", "pyperclip>=1.5.11"]
if sys.version_info < (3, 5):
    install_requires += ["typing"]

# package metadata
setup(
    name="pw",
    version=version,
    description="Search in GPG-encrypted password file.",
    author="Michael Walter",
    author_email="michael.walter@gmail.com",
    url="https://github.com/catch22/pw",
    license="MIT",
    packages=["pw"],
    entry_points={"console_scripts": ["pw = pw.__main__:pw"]},
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    setup_requires=["pytest-runner"],
    install_requires=install_requires,
    extras_require={"dev": ["pytest", "PyYAML", "mypy", "black"]},
)
