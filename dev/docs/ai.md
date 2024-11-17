# The use of AI in Syncademic

Syncademic is a service designed to simplify the integration of university schedules with Google Calendar. It enables students to automatically sync their class schedules from a provided URL, typically linking to an .ICS file, into their personal Google Calendar. By doing so, Syncademic ensures that students can manage all their academic, personal, and professional commitments in one familiar interface, improving planning and conflict avoidance. The service operates in the background, updating schedules in real-time with no manual input, ensuring students never miss any changes. 

# The problem it solves

One could say : “In Google Calendar,  it’s already possible to subscribe to an .ics calendar using an url !”

Yes, but there are some problems : 

- The calendar ics are often exported using the school/university time schedule software (e.g ADE, HyperPlanning) and some are not user friendly. For instance, the events titles of the resulting calendar might be like `IF:5:S1::TCS1:CM::5IF_S1_GR_CM #001` instead of a more pretty `CM - Fondements scientifiques de l'informatique`
- Because there’s not a widely used way to specify colors in an ICS file, (and I doubt the time schedule software would even implement it if it existed), the resulting calendars are of one unique color, instead of having one color per course unit.
- The resulting calendar might contain events that are not relevant for the student. For instance, a calendar might contain all the optional classes, while a student is only affected to a subset.  Plus, deleting those events won’t work, as they will appear again on the next synchronization. Some calendars such as Apple Calendar even restrict the deletion and edition of events

This is why Syncademic is useful : by acting as a middleware between the school’s software and the student’s electronic agenda, we can execute any customization rule and edit titles, add colors, and remvove irrelevant events, or any customization that the user would like. Since Syncademic uses Google Calendar API v3 to insert and update events to the calendar, it’s possible to specify different colors for each event. 

# The concept of rules in Syncademic

In Syncademic, "rules" are user-defined instructions that customize how events from a university's calendar are transformed and synchronized into a student's Google Calendar. Since academic calendars often contain unwieldy or irrelevant information, rules allow us to modify event attributes—such as titles, descriptions, locations, and colors—to make them more user-friendly and personalized.

**Structure of Rules**

A rule consists of two main components:

1. **Conditions**: Criteria that determine whether a rule applies to a particular event. Conditions can be based on event attributes like title, description, or location and can use operators like "equals," "contains," "starts with," "ends with," or even regular expressions. Conditions can be simple or compound, allowing logical combinations (AND, OR) of multiple conditions.
2. **Actions**: Modifications to be applied to events that meet the conditions. Actions can:
    - Change a field (e.g., prepend or append text to the title).
    - Change the event color to categorize or highlight events.
    - Delete events that are irrelevant to the user.

**Implementation**

Rules are defined using JSON structures and are modeled using Pydantic for validation and serialization. This approach ensures that rules are flexible, serializable, and easy to maintain. When Syncademic processes events, it:

- Evaluates each event against the conditions specified in the rules.
- Applies the actions to events that meet the conditions.
- Produces a customized set of events that are then synchronized to the user's Google Calendar.

**Purpose**

The use of rules in Syncademic empowers users to automatically personalize their academic schedules without manual editing. It improves the clarity and relevance of calendar entries by:

- Simplifying complex or cryptic event titles.
- Assigning meaningful colors to different types of events.
- Removing events that the user doesn't need.

By abstracting the customization logic into rules, Syncademic provides a scalable solution that enhances user experience and helps students manage their time more effectively.

## Rules definition

```python
import re
from dataclasses import replace
from typing import Literal, Optional, Self, Union, Sequence

from pydantic import BaseModel, Field, model_validator

from .constants import RulesSettings
from functions.shared.event import Event
from functions.shared.google_calendar_colors import GoogleEventColor

settings = RulesSettings()

EventTextField = Literal["title", "description", "location"]
TextFieldConditionOperator = Literal[
    "equals", "contains", "starts_with", "ends_with", "regex"
]

class TextFieldCondition(BaseModel):
    field: EventTextField
    operator: TextFieldConditionOperator
    value: str = Field(
        ..., min_length=1, max_length=settings.MAX_TEXT_FIELD_VALUE_LENGTH
    )
    case_sensitive: Optional[bool] = True
    negate: Optional[bool] = False

    @model_validator(mode="after")
    def validate_regex(self) -> Self:
        if self.operator == "regex":
            try:
                re.compile(self.value)
            except re.error as e:
                raise ValueError(
                    f"Invalid regular expression: `{self.value}`, error: {e}"
                )
        return self

    def evaluate(self, event: Event) -> bool:
        field_value = getattr(event, self.field)
        assert isinstance(field_value, str)

        condition_value = self.value

        if not self.case_sensitive:
            field_value = field_value.lower()
            condition_value = condition_value.lower()

        match self.operator:
            case "equals":
                result = field_value == condition_value
            case "contains":
                result = condition_value in field_value
            case "starts_with":
                result = field_value.startswith(condition_value)
            case "ends_with":
                result = field_value.endswith(condition_value)
            case "regex":
                flags = 0 if self.case_sensitive else re.IGNORECASE
                result = bool(re.search(condition_value, field_value, flags))
            case _:
                raise ValueError(f"Unimplemented operator: {self.operator}")

        return not result if self.negate else result

CompoundConditionLogicalOperator = Literal["AND", "OR"]

class CompoundCondition(BaseModel):
    logical_operator: CompoundConditionLogicalOperator
    conditions: Sequence["ConditionType"] = Field(
        ..., min_length=2, max_length=settings.MAX_CONDITIONS
    )

    @model_validator(mode="after")
    def validate_nesting_depth(self) -> Self:
        def check_depth(condition, current_depth=1):
            if isinstance(condition, CompoundCondition):
                if current_depth > settings.MAX_NESTING_DEPTH:
                    raise ValueError("Maximum nesting depth exceeded.")
                for cond in condition.conditions:
                    check_depth(cond, current_depth + 1)

        for condition in self.conditions:
            check_depth(condition)

        return self

    def evaluate(self, event: Event) -> bool:
        match self.logical_operator:
            case "AND":
                return all(condition.evaluate(event) for condition in self.conditions)
            case "OR":
                return any(condition.evaluate(event) for condition in self.conditions)

        raise ValueError(f"Unimplemented logical operator: {self.logical_operator}")

ConditionType = Union[TextFieldCondition, CompoundCondition]

CompoundCondition.model_rebuild()

class ChangeFieldAction(BaseModel):
    action: Literal["change_field"] = "change_field"
    field: EventTextField
    method: Literal["set", "append", "prepend"]
    value: str = Field(
        ..., min_length=0, max_length=settings.MAX_TEXT_FIELD_VALUE_LENGTH
    )

    def apply(self, event: Event) -> Optional[Event]:
        field_value = getattr(event, self.field)
        assert isinstance(field_value, str)

        new_value = self.value

        match self.method:
            case "set":
                new_field_value = new_value
            case "append":
                new_field_value = field_value + new_value
            case "prepend":
                new_field_value = new_value + field_value
            case _:
                raise ValueError(f"Unimplemented method: {self.method}")

        return replace(event, **{self.field: new_field_value})

class ChangeColorAction(BaseModel):
    action: Literal["change_color"] = "change_color"
    value: GoogleEventColor

    def apply(self, event: Event) -> Optional[Event]:
        return replace(event, color=self.value)

class DeleteEventAction(BaseModel):
    action: Literal["delete_event"] = "delete_event"

    def apply(self, event: Event) -> Optional[Event]:
        return None

ActionType = ChangeFieldAction | ChangeColorAction | DeleteEventAction

class Rule(BaseModel):
    condition: ConditionType
    actions: Sequence[ActionType] = Field(
        ..., min_length=1, max_length=settings.MAX_ACTIONS
    )

    def apply(self, event: Event) -> Optional[Event]:
        if self.condition.evaluate(event):
            for action in self.actions:
                result = action.apply(event)
                if result is None:
                    return None
                event = result
        return event

class Ruleset(BaseModel):
    rules: Sequence[Rule] = Field(..., min_length=1, max_length=settings.MAX_RULES)

    def apply(self, events: Sequence[Event]) -> list[Event]:
        new_events = []
        for event in events:
            for rule in self.rules:
                event = rule.apply(event)
                if event is None:
                    break
            if event is not None:
                new_events.append(event)
        return new_events

```

## Rules Creation

**The Challenge: Automating Rule Creation for Personalized Schedules**

Creating customized rules for each student's unique timetable is a significant challenge. It's impractical for the Syncademic administrator to manually define these rules for every individual schedule. We need a scalable solution that can handle the diversity of timetables without burdening the users.

**Possible Solutions:**

1. **User-Defined Rules:**
    - **Complexity for Users:** Allowing users to define their own rules would require a sophisticated user interface and assume that users are comfortable with rule creation, which often involves programming concepts.
    - **Limited Accessibility:** Many students may not have the technical background to create effective rules, leading to a poor user experience.
2. **Automated Rule Generation Using AI:**
    - **Leverage LLMs:** Utilize Large Language Models (LLMs) to automatically generate the necessary customization rules.
    - **Input Data:**
        - **Rules Specification:** Provide the LLM with the detailed structure and capabilities of the rules system.
        - **User’s Timetable:** Supply the LLM with the user's schedule data.
        - **User Preferences (Optional):** Include any specific customization preferences expressed in natural language.
    - **Process:**
        - The LLM analyzes the timetable and identifies issues like cryptic titles, lack of colors, or irrelevant events.
        - It generates the appropriate rules in JSON format to transform the timetable accordingly.
        - The generated JSON is validated using Pydantic to ensure it conforms to the expected schema.
        - If validation fails, errors are fed back to the LLM for correction.

**Our Chosen Approach:**

We will implement the second option—automated rule generation using AI. This approach minimizes user effort and expertise required while providing personalized and accurate schedule customizations.

## The Problem of Time Schedule Compression

**The Challenge: Providing Adequate Context to the LLM Within Constraints**

LLMs have limitations on the amount of text (context window) they can process at once. Directly feeding the entire ICS file of a user's timetable is not feasible due to its size and redundancy. However, the LLM requires sufficient context to understand the schedule and generate effective rules.

**Our Solution: Compressing the Timetable Data**

We need to condense the timetable information to include only the most relevant details necessary for rule generation. This "compression" ensures that we stay within the LLM's context limits while providing enough information for meaningful customization.

**Essential Context for the LLM:**

1. **Event Details and Descriptions:**
    - **Understanding Cryptic Titles:** Include samples of event titles and their descriptions to help the LLM decipher and transform unreadable or cryptic titles into user-friendly ones.
    - **Sample Events:** Provide a representative subset of events that highlight common patterns and issues in the timetable.
2. **Global Structure of the Timetable:**
    - **Course Units Overview:** Summarize each course unit with:
        - **Time Span:** Start and end dates of the course.
        - **Event Count:** Number of events associated with the course.
    - **Importance Assessment:** This helps the LLM prioritize courses based on their duration and frequency, which is useful for assigning colors and highlighting.
3. **Conflict Identification:**
    - **Event Overlaps:** Inform the LLM about any scheduling conflicts where events occur simultaneously.
    - **Duplicate Events:**
        - **Detection:** Highlight events that are exact or near duplicates.
        - **Resolution Strategy:** Provide guidelines on which duplicates to remove (e.g., keep the event with more detailed information).
4. **User-Specific Relevance:**
    - **Irrelevant Events:** Identify events that may not be applicable to the user, such as optional classes not enrolled in.
    - **Caution with Deletion:**
        - **Risk Mitigation:** Emphasize the importance of not deleting critical events like exams or mandatory classes.
        - **User Input:** Note that without explicit user instructions, events should generally not be deleted.

**Challenges and Considerations:**

- **Limited Rule Expressiveness:**
    - **Complex Conditions:** The current rules system may not support advanced logic (e.g., conditional dependencies between events).
    - **LLM's Role:** The LLM should recognize these limitations and avoid proposing rules that cannot be implemented, providing explanations when necessary.
- **Balancing Detail and Context Limitations:**
    - **Information Sufficiency:** Ensure that the compressed data still allows the LLM to make accurate and helpful customizations.
    - **Avoiding Overload:** Exclude unnecessary details that do not contribute to rule generation to conserve context space.

**Future Enhancements:**

- **Interactive Sessions:**
    - **User Engagement:** Develop a system where the LLM can ask clarifying questions to the user, gathering additional preferences or resolving ambiguities.
    - **Improved Customization:** This interaction can lead to more precise and personalized rules.
- **Post-Processing Unhandled Events:**
    - **Comprehensive Coverage:** After initial rule application, present any remaining unmodified events to the LLM for further analysis.
    - **Continuous Improvement:** This iterative approach ensures that all aspects of the timetable are optimized.

**Conclusion:**

By intelligently compressing the timetable data and leveraging the capabilities of LLMs, we aim to automate the creation of customization rules effectively. This approach addresses the challenges of individual schedule variations and context limitations while prioritizing user convenience and accuracy.

### Example of time schedule compression

```
Cluster 2 (46 events):
From 2024-09-23 to 2025-01-23 (123 days)

Top terms: promo, edt, if, s1, 5if_s1_gr_cm
Events:
- IF:5:S1::Promo:EDT::5IF_S1_GR_CM #001
- IF:5:S1::Promo:EDT::5IF_S1_GR_CM #002
- IF:5:S1::Promo:EDT::5IF_S1_GR_CM #003
- IF:5:S1::Promo:EDT::5IF_S1_GR_CM #004
- IF:5:S1::Promo:EDT::5IF_S1_GR_CM #028
  ... and 41 more events

Longest description:
```
[IF-5-S1~Promo:EDT] Créneau Promo
(Réunion présentation PFE - https://insa-lyon-fr.zoom.us/j/98963419861?pwd=eUY3bko2QlhpYjY0YlZSbWZhVUpaUT09)

IF:5:S1::Promo:EDT::5IF_S1_GR_CM
MIRANDA Felipe

(Exporté le:21/10/2024 16:15)
```

Cluster 6 (41 events):
From 2024-10-03 to 2025-01-31 (121 days)

Top terms: psat, cm, if, s1, 5if_s1_gr_cm
Events:
- IF:5:S1::PSAT:CM::5IF_S1_GR_CM #040
- IF:5:S1::PSAT:CM::5IF_S1_GR_CM #041
- IF:5:S1::PSAT:CM::5IF_S1_GR_CM #001
- IF:5:S1::PSAT:CM::5IF_S1_GR_CM #004
- IF:5:S1::PSAT:CM::5IF_S1_GR_CM #002
  ... and 36 more events

Longest description:
```
[IF-5-S1-EC-PSAT:CM] Projet de Synthèse Scientifique et Technique
(P-SAT (TD) - Choix des sujets)

IF:5:S1::PSAT:CM::5IF_S1_GR_CM
DURAND Gillaume

(Exporté le:21/10/2024 16:15)
```

Cluster 0 (17 events):
From 2024-09-24 to 2024-11-26 (64 days)

Top terms: ot8, ot, td, mining, 08
Events:
- IF:5:S1::OT8:TD::5IF-OT-08 #008
- IF:5:S1::OT8:TD::5IF-OT-08 #009
- IF:5:S1::OT8:TD::5IF-OT-08 #012
- IF:5:S1::OT8:TD::5IF-OT-08 #010
- IF:5:S1::OT8:TD::5IF-OT-08 #011
  ... and 12 more events

Longest description:
```
[IF-5-S1-EC-OT8:TD] Text mining
(OT 8 - Text mining)

IF:5:S1::OT8:TD::5IF-OT-08
RENARD Pascal-Yves
KOVACS-ZSIGMOND Eloy

(Exporté le:21/10/2024 16:15)
```

Cluster 4 (16 events):
From 2024-10-01 to 2025-02-04 (127 days)

Top terms: eps, edt, if, s1, 5if_s1_gr_cm
Events:
- IF:5:S1::EPS:EDT::5IF_S1_GR_CM #002
- IF:5:S1::EPS:EDT::5IF_S1_GR_CM #003
- IF:5:S1::EPS:EDT::5IF_S1_GR_CM #004
- IF:5:S1::EPS:EDT::5IF_S1_GR_CM #005
- IF:5:S1::EPS:EDT::5IF_S1_GR_CM #006
  ... and 11 more events

Longest description:
```
[IF-5-S1~EPS:EDT] Créneau EPS
()

IF:5:S1::EPS:EDT::5IF_S1_GR_CM

(Exporté le:21/10/2024 16:15)
```

Cluster 3 (14 events):
From 2024-10-01 to 2025-01-21 (113 days)

Top terms: eps, 5a, 07, ma16, cds
Events:
- CDS:EPS:S1::5A:TD::EPS-5-S1-MA16--07 #007
- CDS:EPS:S1::5A:TD::EPS-5-S1-MA16--07 #010
- CDS:EPS:S1::5A:TD::EPS-5-S1-MA16--07 #008
- CDS:EPS:S1::5A:TD::EPS-5-S1-MA16--07 #011
- CDS:EPS:S1::5A:TD::EPS-5-S1-MA16--07 #012
  ... and 9 more events

Longest description:
```
[CDS-EPS-S1-CMP-5A:TD] EPS 5A
()

CDS:EPS:S1::5A:TD::EPS-5-S1-MA16--07 (EPS-5-S1-MA16--07 #THO)
LUCAS Lio

(Exporté le:21/10/2024 16:15)
```

Cluster 5 (12 events):
From 2024-10-23 to 2025-01-15 (85 days)

Top terms: tcs2, cm, simulation, modélisation, systèmes
Events:
- IF:5:S1::TCS2:CM::5IF_S1_GR_CM #008
- IF:5:S1::TCS2:CM::5IF_S1_GR_CM #010
- IF:5:S1::TCS2:CM::5IF_S1_GR_CM #009
- IF:5:S1::TCS2:CM::5IF_S1_GR_CM #011
- IF:5:S1::TCS2:CM::5IF_S1_GR_CM #006
  ... and 7 more events

Longest description:
```
[IF-5-S1-EC-TCS2:EV] Formation par la Recherche : Modélisation et simulation de systèmes
(TCS1 et 2 - DS)

IF:5:S1::TCS2:EV::5IF_S1_GR_CM
DURAND Gillaume

(Exporté le:21/10/2024 16:15)
```

Cluster 7 (12 events):
From 2024-10-01 to 2024-11-12 (43 days)

Top terms: tcs1, cm, fondements, scientifiques, informatique
Events:
- IF:5:S1::TCS1:CM::5IF_S1_GR_CM #012
- IF:5:S1::TCS1:CM::5IF_S1_GR_CM #005
- IF:5:S1::TCS1:CM::5IF_S1_GR_CM #001
- IF:5:S1::TCS1:CM::5IF_S1_GR_CM #002
- IF:5:S1::TCS1:CM::5IF_S1_GR_CM #003
  ... and 7 more events

Longest description:
```
[IF-5-S1-EC-TCS1:CM] Formation par la Recherche : Fondements scientifiques de l'informatique
()

IF:5:S1::TCS1:CM::5IF_S1_GR_CM
DUPRE DE DINECHIN Floran

(Exporté le:21/10/2024 16:15)
```

Cluster 1 (11 events):
From 2024-10-14 to 2025-01-20 (99 days)

Top terms: serie4, hu, opt18, td, s1
Events:
- HU:0:S1::S-SERIE4:TD::SERIE4-OPT18 #001
- HU:0:S1::S-SERIE4:TD::SERIE4-OPT18 #002
- HU:0:S1::S-SERIE4:TD::SERIE4-OPT18 #003
- HU:0:S1::S-SERIE4:TD::SERIE4-OPT18 #004
- HU:0:S1::S-SERIE4:TD::SERIE4-OPT18 #007
  ... and 6 more events

Longest description:
```
[HU-0-S1-EC-S-SERIE4:TD] Options Sciences Humaines et Sociales, S1 Série 4
()

HU:0:S1::S-SERIE4:TD::SERIE4-OPT18
LAVILLE Jean Philippe

(Exporté le:21/10/2024 16:15)
```

Unclustered (5 events):
From 2024-10-02 to 2024-11-20 (49 days)
Events:
- IF:5:S1::MAN-HU:CM::5IF_S1_GR_CM #001
- IF:5:S1::MAN-HU:CM::5IF_S1_GR_CM #002
- Visite UQAC
- IF:5:S1::MAN-HU:CM::5IF_S1_GR_CM #003
- IF:5:S1::MAN-HU:CM::5IF_S1_GR_CM #004

Longest description:
```
[IF-5-S1-EC-MAN-HU:CM] Management d'équipe
(CM - Management)

IF:5:S1::MAN-HU:CM::5IF_S1_GR_CM

(Exporté le:21/10/2024 16:15)
```

```

### Example of rules for the time schedule above

```
{
  "rules": [
    {
      "condition": {
        "field": "title",
        "operator": "contains",
        "value": "PSAT",
        "case_sensitive": true
      },
      "actions": [
        {
          "action": "change_field",
          "field": "title",
          "method": "set",
          "value": "Projet de Synthèse Scientifique et Technique"
        },
        {
          "action": "change_color",
          "value": "banana"
        }
      ]
    },
    {
      "condition": {
        "field": "title",
        "operator": "contains",
        "value": "OT8",
        "case_sensitive": true
      },
      "actions": [
        {
          "action": "change_field",
          "field": "title",
          "method": "set",
          "value": "Text Mining"
        },
        {
          "action": "change_color",
          "value": "tomato"
        }
      ]
    },
    {
      "condition": {
        "field": "title",
        "operator": "contains",
        "value": "EPS",
        "case_sensitive": true
      },
      "actions": [
        {
          "action": "change_field",
          "field": "title",
          "method": "set",
          "value": "Education Physique et Sportive"
        },
        {
          "action": "change_color",
          "value": "tangerine"
        }
      ]
    },
    {
      "condition": {
        "field": "title",
        "operator": "contains",
        "value": "TCS1",
        "case_sensitive": true
      },
      "actions": [
        {
          "action": "change_field",
          "field": "title",
          "method": "set",
          "value": "Fondements scientifiques de l'informatique"
        },
        {
          "action": "change_color",
          "value": "flamingo"
        }
      ]
    },
    {
      "condition": {
        "field": "title",
        "operator": "contains",
        "value": "TCS2",
        "case_sensitive": true
      },
      "actions": [
        {
          "action": "change_field",
          "field": "title",
          "method": "set",
          "value": "Modélisation et simulation de systèmes"
        },
        {
          "action": "change_color",
          "value": "flamingo"
        }
      ]
    },
    {
      "condition": {
        "field": "title",
        "operator": "contains",
        "value": "SERIE4",
        "case_sensitive": true
      },
      "actions": [
        {
          "action": "change_field",
          "field": "title",
          "method": "set",
          "value": "Options Sciences Humaines et Sociales"
        },
        {
          "action": "change_color",
          "value": "peacock"
        }
      ]
    },
    {
      "condition": {
        "field": "title",
        "operator": "contains",
        "value": "MAN-HU",
        "case_sensitive": true
      },
      "actions": [
        {
          "action": "change_field",
          "field": "title",
          "method": "set",
          "value": "Management d'équipe"
        },
        {
          "action": "change_color",
          "value": "sage"
        }
      ]
    },
    {
      "condition": {
        "field": "title",
        "operator": "contains",
        "value": "Promo",
        "case_sensitive": true
      },
      "actions": [
        {
          "action": "change_color",
          "value": "graphite"
        }
      ]
    },
    {
      "condition": {
        "field": "description",
        "operator": "contains",
        "value": ":CM:",
        "case_sensitive": true
      },
      "actions": [
        {
          "action": "change_field",
          "field": "title",
          "method": "prepend",
          "value": "CM - "
        }
      ]
    },
    {
      "condition": {
        "field": "description",
        "operator": "contains",
        "value": ":TD:",
        "case_sensitive": true
      },
      "actions": [
        {
          "action": "change_field",
          "field": "title",
          "method": "prepend",
          "value": "TD - "
        }
      ]
    }
  ]
}
```

## The prompt to create the rules with an LLM

```
Create customization rules in JSON format for personalizing university schedule synchronization with Google Calendar. Use the provided compressed view of the time schedule to generate these rules.

Ensure the generated JSON creates concise and user-friendly schedules by:
- Simplifying event titles to make them easy to read.
- Including the event type in the title (e.g., Lecture, Lab, or Seminar in English; CM, TD, or TP in French) if it can be determined from the context.
- Using different colors for each event type. First, identify the main focus of the time schedule and assign "graphite" (grey) to the less important course units.

Notes: 
- These instructions are in English, but the user's calendar should not switch language. Never translate course unit names if not asked. 
- Rules are applied sequentially. Each event is passed through all rules until no more rules apply.
- Students want different colors for each course unit, not for each event type.

# Output Format
## Brainstorming 
Under `brainstorming`, do the following. 
1.  Analyze the time schedule
    - What's the time schedule base language ? 
    - Are the titles readable ? 
    - What are the different course units, and eventually their abbreviations ? Do not translate the names.
    - Do the title or description contain what kind of event this is ?

2. Brainstorm the rules you plan to write. For each problem to solve, identify the conditions and the actions to solve the titles and colors problems. 

## Final Ruleset
Finally, produce the Ruleset in JSON format.
```

### Function calling

To force the LLM to output its answer in the desired format, we use function calling

This technique provides a structured way to control and shape the model's responses, ensuring they adhere to the desired format. When implementing function calling, I define a schema that specifies the expected output format. This schema acts as a template for the LLM to follow when generating its response.

**JSON Schema**
Function definitions are typically provided to the LLM in a JSON format. This schema includes:

- Function name
- Description of the function's purpose
- Parameters with their types and descriptions

For example:

```json
{
  "name": "output",
  "description": "Output of brainstorming and rules",
  "parameters": {
    "type": "object",
    "properties": {
      "brainstorming": {
        "type": "string",
        "description": "Your brainstorming before creating the rules"
      },
      "ruleset": {
        "type": "string",
        "description": "Ruleset as JSON"
      }
    },
    "required": ["brainstorming", "ruleset"]
  }
}

```

### Importance of the brainstorming

Making an LLM "reason" or "think" before providing an answer is highly important for several reasons:

1. Improved accuracy: Encouraging the LLM to engage in a reasoning process often leads to more accurate and reliable responses. This is particularly evident in complex tasks that require multi-step problem-solving or logical deduction.
2. Enhanced problem-solving: By prompting the LLM to break down problems into steps, it can tackle more complex issues and provide more comprehensive solutions[1]. This approach, known as Chain of Thought (CoT), has shown significant improvements in the reasoning abilities of large language models.
3. Transparency in decision-making: When an LLM shows its reasoning process, it becomes easier for users to understand how it arrived at a particular conclusion. This transparency can increase trust in the model's outputs.
4. Task-dependent benefits: The advantages of increased reasoning steps are particularly pronounced for complex tasks, while simpler tasks may require fewer steps[1]. This suggests that the importance of reasoning varies based on the complexity of the problem at hand.
5. Reduction of errors: By encouraging step-by-step thinking, LLMs are less likely to make hasty conclusions or overlook important details. This can help reduce errors and inconsistencies in their responses.

### Few shot prompting

Few-shot prompting is a technique where a small number of examples are provided to an AI model within the prompt to guide its performance on a specific task. This method leverages the model's ability to learn from context and generalize from the provided examples, allowing it to generate appropriate responses for new, similar inputs without requiring extensive training data.

We use this technique to guide the LLM during the brainstorming step, so it asks itself the right questions and answer them effectively before answering. 

### [Langchain](https://langchain.com)

To implement our AI features in Syncademic, we use the python Langchain library. LangChain is an open-source framework for building applications powered by large language models (LLMs). It provides tools to integrate LLMs with data sources, memory management, and task orchestration, enabling complex workflows like chatbots, summarization, and structured output generation.

**Example: Simplifying Structured Output**
LangChain can generate outputs in a predefined schema, ensuring consistency. Here's a concise example:

```python
from typing import Optional
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI

# Define schema
class Joke(BaseModel):
    setup: str = Field(description="The setup of the joke")
    punchline: str = Field(description="The punchline of the joke")
    rating: Optional[int] = Field(default=None, description="Rating (1-10)")

# Initialize model
llm = ChatOpenAI(model="gpt-4o-mini")

# Bind schema to LLM
structured_llm = llm.with_structured_output(Joke)

# Generate structured output
result = structured_llm.invoke("Tell me a joke about cats")
print(result)  # Outputs: {'setup': ..., 'punchline': ..., 'rating': ...}

```

We use Structured output to ensure that Rules conform to the specification.

### Langsmith

[LangSmith](https://www.langchain.com/langsmith) is a comprehensive developer platform designed to streamline the entire lifecycle of applications powered by large language models (LLMs). It offers tools for debugging, collaboration, testing, and monitoring, enabling developers to build, refine, and deploy LLM applications efficiently. LangSmith is compatible with applications built using LangChain as well as those developed independently, making it a versatile tool for developers working with LLMs.  

### LangGraph

[LangGraph](https://langchain-ai.github.io/langgraph/) is an open-source library that enables developers to build stateful, multi-agent applications using large language models (LLMs). It offers features such as support for cycles and branching, automatic state persistence, human-in-the-loop capabilities, and streaming support, facilitating the creation of complex workflows and robust agent behaviors. 

In the future, we plan to use LangGraph to implement more complex and robust customization options.