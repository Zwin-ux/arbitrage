"""Desktop application layer for market-data-recorder."""

from .app_types import AppProfile, CredentialStatus, EngineStatus, RunPreset
from .controller import EngineController

__version__ = "0.1.2"

__all__ = [
    "AppProfile",
    "CredentialStatus",
    "EngineController",
    "EngineStatus",
    "RunPreset",
    "__version__",
]
