from __future__ import absolute_import, division, print_function
from .store import Entry
import warnings
from typing import Dict, Iterator, List, Union, Text

EXTENSIONS = [".yaml", ".yml"]


def make_entry(key: str, dict: Dict[str, str]) -> Entry:
    notes = " | ".join(str(dict[key]) for key in ["L", "N"] if key in dict)
    return Entry(
        key=key,
        user=str(dict.get("U", "")),
        password=str(dict.get("P", "")),
        notes=notes,
    )


def parse_entries(src: str) -> List[Entry]:
    warnings.warn(
        "YAML support is deprecated and will be removed in the next version",
        DeprecationWarning,
    )
    import yaml

    try:
        from yaml import CLoader as Loader  # type: ignore
    except ImportError:
        from yaml import Loader as Loader  # type: ignore
    root_node = yaml.load(src, Loader=Loader)
    return list(_collect_entries(root_node, ""))


def _collect_entries(
    current_node: Union[List, Dict, Text], current_key: str
) -> Iterator[Entry]:
    # list of accounts?
    if isinstance(current_node, list):
        for child_node in current_node:
            assert isinstance(child_node, dict), "expected list of accounts"
            yield make_entry(current_key, child_node)
        return

    # single acccount?
    if isinstance(current_node, dict) and "P" in current_node:
        yield make_entry(current_key, current_node)
        return

    # single password?
    if not isinstance(current_node, dict):
        yield Entry(key=current_key, user="", password=str(current_node), notes="")
        return

    # otherwise: subtree!
    for key, child_node in current_node.items():
        # ignore entries in parentheses
        if key.startswith("("):
            continue

        # recurse
        for entry in _collect_entries(
            child_node, current_key + "." + key if current_key else key
        ):
            yield entry
