from functions.models.rules import ChangeColorAction, Rule, Ruleset, TextFieldCondition
from functions.shared.google_calendar_colors import GoogleEventColor


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
