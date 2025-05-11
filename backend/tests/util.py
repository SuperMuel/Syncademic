from backend.models.rules import ChangeColorAction, Rule, Ruleset, TextFieldCondition
from backend.shared.google_calendar_colors import GoogleEventColor


VALID_RULESET = Ruleset(
    rules=[
        Rule(
            condition=TextFieldCondition(
                field="title",
                operator="contains",
                value="x",
            ),
            actions=[ChangeColorAction(value=GoogleEventColor.BASIL)],
        )
    ],
)
