from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel, Field

from .app_types import AppProfile, BotBlueprint, BotRecipe


class BotRecipesDocument(BaseModel):
    schema_version: int = 1
    recipes: list[BotRecipe] = Field(default_factory=list)


class BotRecipeStore:
    def recipes_path(self, profile: AppProfile) -> Path:
        return profile.data_dir / "bot_recipes.json"

    def list_local_recipes(self, profile: AppProfile) -> list[BotRecipe]:
        return sorted(
            self._load(profile).recipes,
            key=lambda recipe: (recipe.updated_at, recipe.created_at, recipe.label.lower()),
        )

    def save_recipe(self, profile: AppProfile, recipe: BotRecipe) -> BotRecipe:
        document = self._load(profile)
        now = datetime.now(timezone.utc)
        normalized = recipe.model_copy(deep=True)
        if not normalized.recipe_id:
            normalized.recipe_id = str(uuid.uuid4())
        normalized.profile_id = profile.id
        normalized.updated_at = now
        if normalized.created_at.tzinfo is None:
            normalized.created_at = normalized.created_at.replace(tzinfo=timezone.utc)
        for index, existing in enumerate(document.recipes):
            if existing.recipe_id == normalized.recipe_id:
                document.recipes[index] = normalized
                self._write(profile, document)
                return normalized
        document.recipes.append(normalized)
        self._write(profile, document)
        return normalized

    def recipe_from_blueprint(self, profile: AppProfile, blueprint: BotBlueprint) -> BotRecipe:
        return BotRecipe(
            recipe_id=blueprint.id,
            profile_id=profile.id,
            label=blueprint.label,
            description=blueprint.description,
            strategy_family=blueprint.strategy_family,
            min_net_edge_bps=blueprint.min_net_edge_bps,
            target_stake_cents=blueprint.target_stake_cents,
            max_assignments=blueprint.max_assignments,
            route_preference=blueprint.route_preference,
            lab_only=blueprint.lab_only,
            enabled=True,
            source_kind="starter",
            source_blueprint_id=blueprint.id,
        )

    def fork_recipe(
        self,
        profile: AppProfile,
        recipe: BotRecipe,
        *,
        new_label: str | None = None,
    ) -> BotRecipe:
        now = datetime.now(timezone.utc)
        label = new_label or self._next_fork_label(profile, recipe.label)
        base_source = recipe.source_blueprint_id or recipe.recipe_id
        fork = BotRecipe(
            recipe_id=str(uuid.uuid4()),
            profile_id=profile.id,
            label=label,
            description=f"Local fork of {recipe.label}. {recipe.description}",
            strategy_family=recipe.strategy_family,
            min_net_edge_bps=recipe.min_net_edge_bps,
            target_stake_cents=recipe.target_stake_cents,
            max_assignments=recipe.max_assignments,
            route_preference=recipe.route_preference,
            lab_only=recipe.lab_only,
            enabled=recipe.enabled,
            source_kind="forked",
            source_recipe_id=recipe.recipe_id,
            source_blueprint_id=base_source,
            created_at=now,
            updated_at=now,
        )
        return self.save_recipe(profile, fork)

    def _next_fork_label(self, profile: AppProfile, base_label: str) -> str:
        existing_labels = {recipe.label for recipe in self.list_local_recipes(profile)}
        if f"{base_label} Mk II" not in existing_labels:
            return f"{base_label} Mk II"
        index = 3
        while True:
            candidate = f"{base_label} Mk {index}"
            if candidate not in existing_labels:
                return candidate
            index += 1

    def _load(self, profile: AppProfile) -> BotRecipesDocument:
        path = self.recipes_path(profile)
        if not path.exists():
            return BotRecipesDocument()
        payload = json.loads(path.read_text(encoding="utf-8"))
        document = BotRecipesDocument.model_validate(payload)
        if document.schema_version != 1:
            return BotRecipesDocument(recipes=document.recipes)
        return document

    def _write(self, profile: AppProfile, document: BotRecipesDocument) -> None:
        profile.data_dir.mkdir(parents=True, exist_ok=True)
        path = self.recipes_path(profile)
        path.write_text(document.model_dump_json(indent=2), encoding="utf-8")
