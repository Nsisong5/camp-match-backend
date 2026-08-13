import importlib

import pytest


def test_package_structure():
    modules = [
        "camp_match",
        "camp_match.config",
        "camp_match.shared_kernel",
        "camp_match.shared_kernel.domain",
        "camp_match.shared_kernel.application",
        "camp_match.platform",
        "camp_match.platform.logging",
        "camp_match.platform.errors",
        "camp_match.platform.db",
        "camp_match.modules",
    ]
    for module_name in modules:
        try:
            importlib.import_module(module_name)
        except ImportError as e:
            pytest.fail(f"Module {module_name} could not be imported: {e}")
