"""Expose various directories."""

import sys
from pathlib import Path


TEST_DIR = Path(__file__).parent
RESOURCE_DIR = TEST_DIR / "resources"

sys.path.insert(0, str(RESOURCE_DIR))


def resource(*path_parts) -> Path:
    """Get the absolute path to an resource in the resources directory."""
    return RESOURCE_DIR.joinpath(*path_parts)
