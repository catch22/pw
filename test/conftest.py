import pytest
import os.path
import pw


@pytest.fixture(scope="session")
def dirname():
    return os.path.dirname(os.path.abspath(__file__))


@pytest.fixture(scope="session", autouse=True)
def override_gpg_homedir(dirname):
    pw._gpg._OVERRIDE_HOMEDIR = os.path.join(dirname, "keys")
