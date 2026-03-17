"""Desktop application layer for Superior."""

from .app_types import AppProfile, CredentialStatus, EngineStatus, RunPreset
from .controller import EngineController

__version__ = "0.4.3"

__all__ = [
    "AppProfile",
    "CredentialStatus",
    "EngineController",
    "EngineStatus",
    "RunPreset",
    "__version__",
]
