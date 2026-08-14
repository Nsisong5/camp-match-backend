import subprocess

import pytest


@pytest.mark.architecture
def test_import_boundaries_hold() -> None:
    """
    Enforce architectural boundaries defined in pyproject.toml using import-linter.
    """
    result = subprocess.run(
        ["poetry", "run", "lint-imports"], capture_output=True, text=True, check=False
    )

    assert result.returncode == 0, f"Import boundaries violated:\n{result.stdout}\n{result.stderr}"
