from backend.models.base import CamelCaseModel


class ExampleModel(CamelCaseModel):
    foo_bar: int
    spam: str


def test_model_dump_defaults_to_aliases() -> None:
    model = ExampleModel(foo_bar=1, spam="eggs")

    assert model.model_dump() == {"fooBar": 1, "spam": "eggs"}


def test_model_dump_can_disable_aliases() -> None:
    model = ExampleModel(foo_bar=1, spam="eggs")

    assert model.model_dump(by_alias=False) == {"foo_bar": 1, "spam": "eggs"}


def test_model_dump_json_defaults_to_aliases() -> None:
    model = ExampleModel(foo_bar=1, spam="eggs")

    assert model.model_dump_json() == '{"fooBar":1,"spam":"eggs"}'
