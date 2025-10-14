from typing import Any

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelCaseModel(BaseModel):
    """Base model that keeps Python attributes snake_case while exposing camelCase JSON."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    def model_dump(self, *, by_alias: bool = True, **kwargs: Any) -> dict[str, Any]:
        """Serialize using camelCase aliases by default."""

        return super().model_dump(by_alias=by_alias, **kwargs)

    def model_dump_json(self, *, by_alias: bool = True, **kwargs: Any) -> str:
        """Serialize to JSON using camelCase aliases by default."""

        return super().model_dump_json(by_alias=by_alias, **kwargs)
