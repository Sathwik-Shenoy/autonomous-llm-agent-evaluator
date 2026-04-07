from __future__ import annotations

import importlib
import inspect
import pkgutil

from app.domain.environments.base import BaseEnvironment


def load_environment_plugins(package_name: str = "app.domain.environments.plugins") -> list[BaseEnvironment]:
    loaded: list[BaseEnvironment] = []
    package = importlib.import_module(package_name)

    for module_info in pkgutil.iter_modules(package.__path__, package.__name__ + "."):
        module = importlib.import_module(module_info.name)
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, BaseEnvironment) and obj is not BaseEnvironment:
                loaded.append(obj())
    return loaded
