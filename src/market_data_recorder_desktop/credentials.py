from __future__ import annotations

import json
from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Protocol

from .app_types import CredentialField, CredentialStatus, CredentialValidationResult


class KeyringBackend(Protocol):
    def get_password(self, service_name: str, username: str) -> str | None: ...

    def set_password(self, service_name: str, username: str, password: str) -> None: ...

    def delete_password(self, service_name: str, username: str) -> None: ...


class CredentialProvider(ABC):
    provider_id: str
    provider_label: str
    docs_url: str

    @abstractmethod
    def fields(self) -> list[CredentialField]:
        raise NotImplementedError

    @abstractmethod
    def validate_payload(self, payload: dict[str, str]) -> CredentialValidationResult:
        raise NotImplementedError


class PolymarketCredentialProvider(CredentialProvider):
    provider_id = "polymarket"
    provider_label = "Polymarket"
    docs_url = "https://docs.polymarket.com/developers/CLOB/authentication"

    def fields(self) -> list[CredentialField]:
        return [
            CredentialField(
                key="wallet_private_key",
                label="Wallet private key",
                help_text="Optional if you already use L2 API credentials. Stored locally only.",
                secret=True,
                multiline=True,
            ),
            CredentialField(
                key="api_key",
                label="API key",
                help_text="Optional if you use only wallet auth. Pair with secret and passphrase.",
                placeholder="pk_live_...",
            ),
            CredentialField(
                key="api_secret",
                label="API secret",
                help_text="Stored locally only.",
                secret=True,
            ),
            CredentialField(
                key="api_passphrase",
                label="API passphrase",
                help_text="Stored locally only.",
                secret=True,
            ),
        ]

    def validate_payload(self, payload: dict[str, str]) -> CredentialValidationResult:
        wallet_private_key = payload.get("wallet_private_key", "").strip()
        api_key = payload.get("api_key", "").strip()
        api_secret = payload.get("api_secret", "").strip()
        api_passphrase = payload.get("api_passphrase", "").strip()
        if not wallet_private_key and not api_key and not api_secret and not api_passphrase:
            return CredentialValidationResult(
                ok=False,
                status="missing",
                message="No Polymarket credentials stored yet.",
            )
        if wallet_private_key:
            return CredentialValidationResult(
                ok=True,
                status="validated",
                message="Wallet-based Polymarket credentials look complete.",
            )
        if api_key and api_secret and api_passphrase:
            return CredentialValidationResult(
                ok=True,
                status="validated",
                message="API-key-based Polymarket credentials look complete.",
            )
        return CredentialValidationResult(
            ok=False,
            status="invalid",
            message="Use either a wallet private key or the full API key/secret/passphrase trio.",
        )


class KalshiCredentialProvider(CredentialProvider):
    provider_id = "kalshi"
    provider_label = "Kalshi"
    docs_url = "https://docs.kalshi.com/getting_started/api_keys"

    def fields(self) -> list[CredentialField]:
        return [
            CredentialField(
                key="api_key_id",
                label="API key ID",
                help_text="The key identifier from your Kalshi API settings.",
                required=True,
                placeholder="prod_...",
            ),
            CredentialField(
                key="private_key_pem",
                label="Private key (PEM)",
                help_text="Paste the PEM contents. Stored locally only.",
                secret=True,
                multiline=True,
                required=True,
            ),
        ]

    def validate_payload(self, payload: dict[str, str]) -> CredentialValidationResult:
        api_key_id = payload.get("api_key_id", "").strip()
        private_key_pem = payload.get("private_key_pem", "").strip()
        if not api_key_id and not private_key_pem:
            return CredentialValidationResult(
                ok=False,
                status="missing",
                message="No Kalshi credentials stored yet.",
            )
        if api_key_id and private_key_pem:
            return CredentialValidationResult(
                ok=True,
                status="validated",
                message="Kalshi credentials look complete.",
            )
        return CredentialValidationResult(
            ok=False,
            status="invalid",
            message="Kalshi credentials require both API key ID and private PEM text.",
        )


class CoachCredentialProvider(CredentialProvider):
    provider_id = "coach"
    provider_label = "Copilot"
    docs_url = "https://github.com/Zwin-ux/arbitrage/tree/main/docs"

    def fields(self) -> list[CredentialField]:
        return [
            CredentialField(
                key="provider_name",
                label="Provider name",
                help_text="Optional note so you remember which model provider this key belongs to.",
                placeholder="OpenAI-compatible, Anthropic, Gemini, or Ollama",
            ),
            CredentialField(
                key="model_name",
                label="Model name",
                help_text="Optional. Used only for Copilot labeling in v1.",
                placeholder="gpt-4o-mini or similar",
            ),
            CredentialField(
                key="api_key",
                label="API key",
                help_text="Stored locally only. Copilot never uses this key to place trades.",
                secret=True,
                required=True,
            ),
        ]

    def validate_payload(self, payload: dict[str, str]) -> CredentialValidationResult:
        api_key = payload.get("api_key", "").strip()
        if not api_key:
            return CredentialValidationResult(
                ok=False,
                status="missing",
                message="No Copilot API key stored yet.",
            )
        return CredentialValidationResult(
            ok=True,
            status="validated",
            message="Copilot key looks complete. Copilot mode still remains read-only.",
        )


class FinancialBenchmarkCredentialProvider(CredentialProvider):
    provider_id = "financial_benchmark"
    provider_label = "Financial benchmark"
    docs_url = "https://docs.financialdatasets.ai"

    def fields(self) -> list[CredentialField]:
        return [
            CredentialField(
                key="provider_name",
                label="Provider name",
                help_text="Optional label for the external benchmark data provider.",
                placeholder="Financial Datasets",
            ),
            CredentialField(
                key="api_key",
                label="API key",
                help_text="Stored locally only. Used for Lab-only benchmark sync and audit.",
                secret=True,
                required=True,
            ),
        ]

    def validate_payload(self, payload: dict[str, str]) -> CredentialValidationResult:
        api_key = payload.get("api_key", "").strip()
        if not api_key:
            return CredentialValidationResult(
                ok=False,
                status="missing",
                message="No financial benchmark API key stored yet.",
            )
        return CredentialValidationResult(
            ok=True,
            status="validated",
            message="Financial benchmark key looks complete. Benchmark data stays audit-only in v1.",
        )


class CredentialVault:
    def __init__(
        self,
        *,
        service_name: str = "market-data-recorder",
        backend: KeyringBackend | None = None,
        providers: Iterable[CredentialProvider] | None = None,
    ):
        if backend is None:
            import keyring

            backend = keyring
        self._backend = backend
        self._service_name = service_name
        provider_items = providers or [
            PolymarketCredentialProvider(),
            KalshiCredentialProvider(),
            CoachCredentialProvider(),
            FinancialBenchmarkCredentialProvider(),
        ]
        self._providers = {provider.provider_id: provider for provider in provider_items}

    def providers(self) -> list[CredentialProvider]:
        return list(self._providers.values())

    def provider(self, provider_id: str) -> CredentialProvider:
        return self._providers[provider_id]

    def save(self, profile_id: str, provider_id: str, payload: dict[str, str]) -> CredentialValidationResult:
        provider = self.provider(provider_id)
        normalized = {key: value for key, value in payload.items() if value.strip()}
        if not normalized:
            return CredentialValidationResult(
                ok=False,
                status="missing",
                message="No credentials entered. Nothing was saved.",
            )
        validation = provider.validate_payload(normalized)
        if validation.status == "invalid":
            return validation
        self._backend.set_password(
            self._service_name,
            self._username(profile_id, provider_id),
            json.dumps(normalized),
        )
        return CredentialValidationResult(
            ok=validation.ok,
            status="saved" if validation.status == "missing" else validation.status,
            message="Credentials stored locally in the OS keychain.",
        )

    def load(self, profile_id: str, provider_id: str) -> dict[str, str]:
        payload = self._backend.get_password(
            self._service_name,
            self._username(profile_id, provider_id),
        )
        if payload is None:
            return {}
        return dict(json.loads(payload))

    def delete(self, profile_id: str, provider_id: str) -> None:
        try:
            self._backend.delete_password(self._service_name, self._username(profile_id, provider_id))
        except Exception:
            return

    def status(self, profile_id: str, provider_id: str) -> CredentialStatus:
        provider = self.provider(provider_id)
        payload = self.load(profile_id, provider_id)
        validation = provider.validate_payload(payload)
        status = validation.status
        if payload and status == "missing":
            status = "saved"
        return CredentialStatus(
            provider_id=provider.provider_id,
            provider_label=provider.provider_label,
            status=status,
            message=validation.message if payload else f"No {provider.provider_label} credentials saved.",
        )

    def statuses_for_profile(self, profile_id: str) -> list[CredentialStatus]:
        return [self.status(profile_id, provider_id) for provider_id in self._providers]

    @staticmethod
    def _username(profile_id: str, provider_id: str) -> str:
        return f"{profile_id}:{provider_id}"
