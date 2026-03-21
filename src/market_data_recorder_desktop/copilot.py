from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable

import httpx

from .app_types import AgentDraft, AgentRequest, LLMProviderId, ModelPreset, ProviderHealth


def _trim_base_url(value: str) -> str:
    return value.rstrip("/")


def default_model_presets() -> list[ModelPreset]:
    return [
        ModelPreset(
            provider_id="none",
            label="Skip for now",
            model_name="",
            base_url="",
            api_key_required=False,
        ),
        ModelPreset(
            provider_id="openai_compatible",
            label="OpenAI-compatible",
            model_name="gpt-4o-mini",
            base_url="https://api.openai.com/v1",
            api_key_required=True,
        ),
        ModelPreset(
            provider_id="anthropic",
            label="Anthropic",
            model_name="claude-3-5-haiku-latest",
            base_url="https://api.anthropic.com",
            api_key_required=True,
        ),
        ModelPreset(
            provider_id="gemini",
            label="Gemini",
            model_name="gemini-2.0-flash",
            base_url="https://generativelanguage.googleapis.com",
            api_key_required=True,
        ),
        ModelPreset(
            provider_id="ollama",
            label="Ollama / local",
            model_name="llama3.2:latest",
            base_url="http://localhost:11434",
            api_key_required=False,
        ),
    ]


class ModelProvider(ABC):
    provider_id: LLMProviderId
    provider_label: str

    def __init__(self, client_factory: Callable[[], httpx.Client] | None = None) -> None:
        self._client_factory = client_factory or (lambda: httpx.Client(timeout=6.0))

    @abstractmethod
    def preset(self) -> ModelPreset:
        raise NotImplementedError

    @abstractmethod
    def health(self, *, model_name: str, base_url: str, api_key: str) -> ProviderHealth:
        raise NotImplementedError

    @abstractmethod
    def complete(
        self,
        *,
        model_name: str,
        base_url: str,
        api_key: str,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        raise NotImplementedError


class OpenAICompatibleProvider(ModelProvider):
    provider_id: LLMProviderId = "openai_compatible"
    provider_label = "OpenAI-compatible"

    def preset(self) -> ModelPreset:
        return next(preset for preset in default_model_presets() if preset.provider_id == self.provider_id)

    def health(self, *, model_name: str, base_url: str, api_key: str) -> ProviderHealth:
        if not api_key.strip():
            return ProviderHealth(
                provider_id=self.provider_id,
                provider_label=self.provider_label,
                status="missing_key",
                message="Add an API key to use this provider.",
                model_name=model_name,
                base_url=base_url,
            )
        if not model_name.strip():
            return ProviderHealth(
                provider_id=self.provider_id,
                provider_label=self.provider_label,
                status="invalid_config",
                message="Choose a model name first.",
                model_name=model_name,
                base_url=base_url,
            )
        target = _trim_base_url(base_url or self.preset().base_url)
        try:
            with self._client_factory() as client:
                response = client.get(
                    f"{target}/models",
                    headers={"Authorization": f"Bearer {api_key.strip()}"},
                )
                response.raise_for_status()
        except Exception as exc:
            return ProviderHealth(
                provider_id=self.provider_id,
                provider_label=self.provider_label,
                status="offline",
                message=f"Could not reach the provider: {exc}",
                model_name=model_name,
                base_url=target,
            )
        return ProviderHealth(
            provider_id=self.provider_id,
            provider_label=self.provider_label,
            status="ready",
            message="Provider is reachable and ready.",
            model_name=model_name,
            base_url=target,
        )

    def complete(
        self,
        *,
        model_name: str,
        base_url: str,
        api_key: str,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        target = _trim_base_url(base_url or self.preset().base_url)
        with self._client_factory() as client:
            response = client.post(
                f"{target}/chat/completions",
                headers={"Authorization": f"Bearer {api_key.strip()}"},
                json={
                    "model": model_name,
                    "temperature": 0.2,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                },
            )
            response.raise_for_status()
            payload = response.json()
        content = payload["choices"][0]["message"]["content"]
        if isinstance(content, str):
            return content.strip()
        if isinstance(content, list):
            parts = [item.get("text", "") for item in content if isinstance(item, dict)]
            return "\n".join(part for part in parts if part).strip()
        return str(content).strip()


class AnthropicProvider(ModelProvider):
    provider_id: LLMProviderId = "anthropic"
    provider_label = "Anthropic"

    def preset(self) -> ModelPreset:
        return next(preset for preset in default_model_presets() if preset.provider_id == self.provider_id)

    def health(self, *, model_name: str, base_url: str, api_key: str) -> ProviderHealth:
        if not api_key.strip():
            return ProviderHealth(
                provider_id=self.provider_id,
                provider_label=self.provider_label,
                status="missing_key",
                message="Add an API key to use this provider.",
                model_name=model_name,
                base_url=base_url,
            )
        if not model_name.strip():
            return ProviderHealth(
                provider_id=self.provider_id,
                provider_label=self.provider_label,
                status="invalid_config",
                message="Choose a model name first.",
                model_name=model_name,
                base_url=base_url,
            )
        target = _trim_base_url(base_url or self.preset().base_url)
        try:
            with self._client_factory() as client:
                response = client.post(
                    f"{target}/v1/messages",
                    headers={
                        "x-api-key": api_key.strip(),
                        "anthropic-version": "2023-06-01",
                    },
                    json={
                        "model": model_name,
                        "max_tokens": 1,
                        "messages": [{"role": "user", "content": "ping"}],
                    },
                )
                response.raise_for_status()
        except Exception as exc:
            return ProviderHealth(
                provider_id=self.provider_id,
                provider_label=self.provider_label,
                status="offline",
                message=f"Could not reach the provider: {exc}",
                model_name=model_name,
                base_url=target,
            )
        return ProviderHealth(
            provider_id=self.provider_id,
            provider_label=self.provider_label,
            status="ready",
            message="Provider is reachable and ready.",
            model_name=model_name,
            base_url=target,
        )

    def complete(
        self,
        *,
        model_name: str,
        base_url: str,
        api_key: str,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        target = _trim_base_url(base_url or self.preset().base_url)
        with self._client_factory() as client:
            response = client.post(
                f"{target}/v1/messages",
                headers={
                    "x-api-key": api_key.strip(),
                    "anthropic-version": "2023-06-01",
                },
                json={
                    "model": model_name,
                    "system": system_prompt,
                    "max_tokens": 400,
                    "messages": [{"role": "user", "content": user_prompt}],
                },
            )
            response.raise_for_status()
            payload = response.json()
        content = payload.get("content", [])
        parts = [item.get("text", "") for item in content if isinstance(item, dict)]
        return "\n".join(part for part in parts if part).strip()


class GeminiProvider(ModelProvider):
    provider_id: LLMProviderId = "gemini"
    provider_label = "Gemini"

    def preset(self) -> ModelPreset:
        return next(preset for preset in default_model_presets() if preset.provider_id == self.provider_id)

    def health(self, *, model_name: str, base_url: str, api_key: str) -> ProviderHealth:
        if not api_key.strip():
            return ProviderHealth(
                provider_id=self.provider_id,
                provider_label=self.provider_label,
                status="missing_key",
                message="Add an API key to use this provider.",
                model_name=model_name,
                base_url=base_url,
            )
        if not model_name.strip():
            return ProviderHealth(
                provider_id=self.provider_id,
                provider_label=self.provider_label,
                status="invalid_config",
                message="Choose a model name first.",
                model_name=model_name,
                base_url=base_url,
            )
        target = _trim_base_url(base_url or self.preset().base_url)
        try:
            with self._client_factory() as client:
                response = client.post(
                    f"{target}/v1beta/models/{model_name}:generateContent",
                    params={"key": api_key.strip()},
                    json={"contents": [{"parts": [{"text": "ping"}]}]},
                )
                response.raise_for_status()
        except Exception as exc:
            return ProviderHealth(
                provider_id=self.provider_id,
                provider_label=self.provider_label,
                status="offline",
                message=f"Could not reach the provider: {exc}",
                model_name=model_name,
                base_url=target,
            )
        return ProviderHealth(
            provider_id=self.provider_id,
            provider_label=self.provider_label,
            status="ready",
            message="Provider is reachable and ready.",
            model_name=model_name,
            base_url=target,
        )

    def complete(
        self,
        *,
        model_name: str,
        base_url: str,
        api_key: str,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        target = _trim_base_url(base_url or self.preset().base_url)
        with self._client_factory() as client:
            response = client.post(
                f"{target}/v1beta/models/{model_name}:generateContent",
                params={"key": api_key.strip()},
                json={
                    "systemInstruction": {"parts": [{"text": system_prompt}]},
                    "contents": [{"parts": [{"text": user_prompt}]}],
                },
            )
            response.raise_for_status()
            payload = response.json()
        candidates = payload.get("candidates", [])
        if not candidates:
            return ""
        parts = candidates[0].get("content", {}).get("parts", [])
        texts = [item.get("text", "") for item in parts if isinstance(item, dict)]
        return "\n".join(part for part in texts if part).strip()


class OllamaProvider(ModelProvider):
    provider_id: LLMProviderId = "ollama"
    provider_label = "Ollama / local"

    def preset(self) -> ModelPreset:
        return next(preset for preset in default_model_presets() if preset.provider_id == self.provider_id)

    def health(self, *, model_name: str, base_url: str, api_key: str) -> ProviderHealth:
        del api_key
        if not model_name.strip():
            return ProviderHealth(
                provider_id=self.provider_id,
                provider_label=self.provider_label,
                status="invalid_config",
                message="Choose a local model name first.",
                model_name=model_name,
                base_url=base_url,
            )
        target = _trim_base_url(base_url or self.preset().base_url)
        try:
            with self._client_factory() as client:
                response = client.get(f"{target}/api/tags")
                response.raise_for_status()
        except Exception as exc:
            return ProviderHealth(
                provider_id=self.provider_id,
                provider_label=self.provider_label,
                status="offline",
                message=f"Could not reach Ollama: {exc}",
                model_name=model_name,
                base_url=target,
            )
        return ProviderHealth(
            provider_id=self.provider_id,
            provider_label=self.provider_label,
            status="ready",
            message="Local model runtime is reachable.",
            model_name=model_name,
            base_url=target,
        )

    def complete(
        self,
        *,
        model_name: str,
        base_url: str,
        api_key: str,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        del api_key
        target = _trim_base_url(base_url or self.preset().base_url)
        with self._client_factory() as client:
            response = client.post(
                f"{target}/api/chat",
                json={
                    "model": model_name,
                    "stream": False,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                },
            )
            response.raise_for_status()
            payload = response.json()
        return str(payload.get("message", {}).get("content", "")).strip()


class CopilotRuntime:
    def __init__(
        self,
        providers: list[ModelProvider] | None = None,
        client_factory: Callable[[], httpx.Client] | None = None,
    ) -> None:
        built_providers = providers or [
            OpenAICompatibleProvider(client_factory),
            AnthropicProvider(client_factory),
            GeminiProvider(client_factory),
            OllamaProvider(client_factory),
        ]
        self._providers = {provider.provider_id: provider for provider in built_providers}

    def presets(self) -> list[ModelPreset]:
        return default_model_presets()

    def provider(self, provider_id: LLMProviderId) -> ModelProvider | None:
        return self._providers.get(provider_id)

    def health(
        self,
        *,
        provider_id: LLMProviderId,
        model_name: str,
        base_url: str,
        api_key: str,
    ) -> ProviderHealth:
        if provider_id == "none":
            return ProviderHealth(
                provider_id="none",
                provider_label="Skip for now",
                status="invalid_config",
                message="No copilot model configured yet. Superior will stay local-first.",
                model_name=model_name,
                base_url=base_url,
            )
        provider = self.provider(provider_id)
        if provider is None:
            return ProviderHealth(
                provider_id=provider_id,
                provider_label=provider_id.replace("_", " ").title(),
                status="invalid_config",
                message="Unknown provider selection.",
                model_name=model_name,
                base_url=base_url,
            )
        return provider.health(model_name=model_name, base_url=base_url, api_key=api_key)

    def rewrite_response(
        self,
        *,
        request: AgentRequest,
        base_text: str,
        draft: AgentDraft | None,
        api_key: str,
    ) -> tuple[str, bool, ProviderHealth]:
        health = self.health(
            provider_id=request.provider_config.provider_id,
            model_name=request.provider_config.model_name,
            base_url=request.provider_config.base_url,
            api_key=api_key,
        )
        if health.status != "ready":
            return base_text, False, health
        provider = self.provider(request.provider_config.provider_id)
        assert provider is not None
        draft_summary = draft.summary if draft is not None else "No draft is attached."
        prompt = (
            "Rewrite this desktop-copilot answer so it stays friendly, concise, and concrete. "
            "Do not add claims, do not invent actions, and do not mention trading live. "
            f"Skill: {request.skill_id}\n"
            f"User question: {request.question}\n"
            f"Selected route: {request.context.selected_route_summary or 'none'}\n"
            f"Setup: {request.context.loadout_summary or 'none'}\n"
            f"Base answer:\n{base_text}\n\n"
            f"Draft summary:\n{draft_summary}"
        )
        try:
            rewritten = provider.complete(
                model_name=request.provider_config.model_name,
                base_url=request.provider_config.base_url,
                api_key=api_key,
                system_prompt=(
                    "You are Superior Copilot, a read-only desktop helper for practice-first event-market bot testing. "
                    "You explain, summarize, and draft safe practice-mode configuration changes. "
                    "Never suggest live execution or guaranteed profits."
                ),
                user_prompt=prompt,
            )
        except Exception as exc:
            return (
                base_text,
                False,
                health.model_copy(update={"status": "offline", "message": f"Remote model failed: {exc}"}),
            )
        return rewritten or base_text, True, health
