from functions.rules.models import Ruleset
from pydantic import BaseModel


class RulesetOutput(BaseModel):
    brainstorming: str
    ruleset: Ruleset