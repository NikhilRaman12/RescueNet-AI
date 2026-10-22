"""Keep pytest writes away from a developer's local operational database."""

import os
import tempfile
from pathlib import Path


def pytest_configure():
    if os.getenv("RESCUENET_DB_PATH"):
        return

    test_data_dir = Path(tempfile.mkdtemp(prefix="rescuenet-pytest-"))
    os.environ["RESCUENET_DB_PATH"] = str(test_data_dir / "rescuenet.db")
