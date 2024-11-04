from functions.ai.types import RulesetOutput
from functions.rules.models import Ruleset


SYSTEM_PROMPT = """Create customization rules in JSON format for personalizing university schedule synchronization with Google Calendar. Use the provided compressed view of the time schedule to generate these rules.

Ensure the generated JSON creates concise and user-friendly schedules by:

- Simplifying event titles to make them easy to read.

- Including the event type in the title (e.g., Lecture, Lab, or Seminar in English; CM, TD, or TP in French) if it can be determined from the context.

- Using different colors for each course unit so that each has a distinct color. Identify the main focus of the time schedule and assign "graphite" (grey) to the less important course units.

**Notes:**

- These instructions are in English, but the user's calendar should not switch language. Never translate course unit names unless specifically asked.

- Rules are applied sequentially. Each event is passed through all rules until no more rules apply.

- Students want different colors for each course unit, not for each event type.

- Event colors default to grey.

---

# Output Format

## Brainstorming

Under `brainstorming`, perform the following detailed analysis:

1. **Analyze the Time Schedule:**

   - **Language Identification:**

     - Determine the base language of the time schedule. Provide evidence from the text to support your conclusion.

   - **Title Readability:**

     - Assess whether the event titles are readable and user-friendly. Identify any abbreviations or codes that may be unclear.

   - **Course Units and Abbreviations:**

     - List all the different course units present in the schedule along with their abbreviations. Do not translate the names. Explain how you identified them.

   - **Event Type Identification:**

     - Determine if the event type (e.g., CM, TD, TP) is indicated in the title or description. Explain how you can identify the event type from the available information.
     - If no event types can be identified, mention that. In this case, don't change the titles.

2. **Brainstorming Rules:**

   - **Problem Identification:**

     - Identify specific problems that need to be addressed in the schedule (e.g., cryptic titles, lack of colors, unclear event types).

   - **Rule Development:**
     - For each problem identified, determine if it can be solved.

     - For each solvable problem, explain the conditions and actions you plan to implement to solve it. Provide reasoning for your choices.

     - Consider how the rules will be applied sequentially and how they will interact.

   - **Color Assignment:**

     - Decide on color assignments for each course unit. Justify your choices, especially in distinguishing main focus areas from less important ones.

## Final Ruleset

Finally, produce the Ruleset in JSON format, ensuring it adheres to the specified structure and addresses all the issues identified in your brainstorming.
"""

EXAMPLE_COMPRESSION_1 = """Cluster 3 (47 events):

From 2024-09-23 to 2025-01-23 (123 days)

Top terms for Cluster 3:

promo, edt, if, s1, 5if_s1_gr_cm, 16, créneau, shs, série, entreprises

Events:

- IF:5:S1::Promo:EDT::5IF_S1_GR_CM #001

- IF:5:S1::Promo:EDT::5IF_S1_GR_CM #002

- IF:5:S1::Promo:EDT::5IF_S1_GR_CM #003

- IF:5:S1::Promo:EDT::5IF_S1_GR_CM #004

- IF:5:S1::Promo:EDT::5IF_S1_GR_CM #028

  ... and 42 more events

Longest description:

---

[IF-5-S1~Promo:EDT] Créneau Promo

(Réunion présentation PFE - https://insa-lyon-fr.zoom.us/j/98963419861?pwd=eUY3bko2QlhpYjY0YlZSbWZhVUpaUT09)

IF:5:S1::Promo:EDT::5IF_S1_GR_CM

LAMARRE Philippe

(Exporté le:16/10/2024 16:59)

---

Cluster 5 (41 events):

From 2024-10-03 to 2025-01-31 (121 days)

Top terms for Cluster 5:

psat, cm, if, s1, 5if_s1_gr_cm, projet, scientifique, synthèse, technique, sat

Events:

- IF:5:S1::PSAT:CM::5IF_S1_GR_CM #040

- IF:5:S1::PSAT:CM::5IF_S1_GR_CM #041

- IF:5:S1::PSAT:CM::5IF_S1_GR_CM #001

- IF:5:S1::PSAT:CM::5IF_S1_GR_CM #004

- IF:5:S1::PSAT:CM::5IF_S1_GR_CM #002

  ... and 36 more events

Longest description:

---

[IF-5-S1-EC-PSAT:CM] Projet de Synthèse Scientifique et Technique

(P-SAT (TD) - Choix des sujets)

IF:5:S1::PSAT:CM::5IF_S1_GR_CM

BESLON Guillaume

(Exporté le:16/10/2024 16:59)

---

Cluster 0 (17 events):

From 2024-09-24 to 2024-11-26 (64 days)

Top terms for Cluster 0:

ot, ot8, td, 5if, mining, text, 08, if, elod, egyed

Events:

- IF:5:S1::OT8:TD::5IF-OT-08 #008

- IF:5:S1::OT8:TD::5IF-OT-08 #009

- IF:5:S1::OT8:TD::5IF-OT-08 #012

- IF:5:S1::OT8:TD::5IF-OT-08 #010

- IF:5:S1::OT8:TD::5IF-OT-08 #011

  ... and 12 more events

Longest description:

---

[IF-5-S1-EC-OT8:TD] Text mining

(OT 8 - Text mining)

IF:5:S1::OT8:TD::5IF-OT-08

GENEST Pierre-Yves

EGYED-ZSIGMOND Elod

(Exporté le:16/10/2024 16:59)

---

Cluster 4 (16 events):

From 2024-10-01 to 2025-02-04 (127 days)

Top terms for Cluster 4:

eps, edt, if, s1, 5if_s1_gr_cm, 16, créneau, exporté, 10, le

Events:

- IF:5:S1::EPS:EDT::5IF_S1_GR_CM #002

- IF:5:S1::EPS:EDT::5IF_S1_GR_CM #003

- IF:5:S1::EPS:EDT::5IF_S1_GR_CM #004

- IF:5:S1::EPS:EDT::5IF_S1_GR_CM #005

- IF:5:S1::EPS:EDT::5IF_S1_GR_CM #006

  ... and 11 more events

Longest description:

---

[IF-5-S1~EPS:EDT] Créneau EPS

()

IF:5:S1::EPS:EDT::5IF_S1_GR_CM

(Exporté le:16/10/2024 16:59)

---

Cluster 2 (12 events):

From 2024-10-23 to 2025-01-15 (85 days)

Top terms for Cluster 2:

tcs2, cm, systèmes, modélisation, simulation, if, s1, guillaume, beslon, formation

Events:

- IF:5:S1::TCS2:CM::5IF_S1_GR_CM #008

- IF:5:S1::TCS2:CM::5IF_S1_GR_CM #010

- IF:5:S1::TCS2:CM::5IF_S1_GR_CM #009

- IF:5:S1::TCS2:CM::5IF_S1_GR_CM #011

- IF:5:S1::TCS2:CM::5IF_S1_GR_CM #006

  ... and 7 more events

Longest description:

---

[IF-5-S1-EC-TCS2:EV] Formation par la Recherche : Modélisation et simulation de systèmes

(TCS1 et 2 - DS)

IF:5:S1::TCS2:EV::5IF_S1_GR_CM

BESLON Guillaume

(Exporté le:16/10/2024 16:59)

---

Cluster 6 (12 events):

From 2024-10-01 to 2024-11-12 (43 days)

Top terms for Cluster 6:

tcs1, cm, scientifiques, fondements, informatique, if, christine, solnon, s1, recherche

Events:

- IF:5:S1::TCS1:CM::5IF_S1_GR_CM #012

- IF:5:S1::TCS1:CM::5IF_S1_GR_CM #005

- IF:5:S1::TCS1:CM::5IF_S1_GR_CM #001

- IF:5:S1::TCS1:CM::5IF_S1_GR_CM #002

- IF:5:S1::TCS1:CM::5IF_S1_GR_CM #003

  ... and 7 more events

Longest description:

---

[IF-5-S1-EC-TCS1:CM] Formation par la Recherche : Fondements scientifiques de l'informatique

()

IF:5:S1::TCS1:CM::5IF_S1_GR_CM

DUPONT DE DINECHIN Florent

(Exporté le:16/10/2024 16:59)

---

Cluster 1 (11 events):

From 2024-10-14 to 2025-01-20 (99 days)

Top terms for Cluster 1:

serie4, hu, td, opt18, s1, sciences, neuville, options, jean, humaines

Events:

- HU:0:S1::S-SERIE4:TD::SERIE4-OPT18 #001

- HU:0:S1::S-SERIE4:TD::SERIE4-OPT18 #002

- HU:0:S1::S-SERIE4:TD::SERIE4-OPT18 #003

- HU:0:S1::S-SERIE4:TD::SERIE4-OPT18 #004

- HU:0:S1::S-SERIE4:TD::SERIE4-OPT18 #007

  ... and 6 more events

Longest description:

---

[HU-0-S1-EC-S-SERIE4:TD] Options Sciences Humaines et Sociales, S1 Série 4

()

HU:0:S1::S-SERIE4:TD::SERIE4-OPT18

NEUVILLE Jean Philippe

(Exporté le:16/10/2024 16:59)

---

Unclustered (4 events):

From 2024-10-22 to 2024-11-20 (30 days)

Events:

- IF:5:S1::MAN-HU:CM::5IF_S1_GR_CM #001

- IF:5:S1::MAN-HU:CM::5IF_S1_GR_CM #002

- IF:5:S1::MAN-HU:CM::5IF_S1_GR_CM #003

- IF:5:S1::MAN-HU:CM::5IF_S1_GR_CM #004

Longest description:

---

[IF-5-S1-EC-MAN-HU:CM] Management d'équipe

(CM - Management)

IF:5:S1::MAN-HU:CM::5IF_S1_GR_CM

(Exporté le:16/10/2024 16:59)

---
"""


EXAMPLE_OUTPUT_1 = RulesetOutput(
    brainstorming="""**1. Analyze the Time Schedule:**

- **Language Identification:**

  - **Reasoning:** The time schedule contains terms like "Créneau", "Réunion présentation", and "Formation par la Recherche". These phrases suggest a French context. Given that many abbreviations are derived from French words and that event titles appear in French, the primary language of this schedule is likely French.

  - **Conclusion:** The base language of the time schedule is **French**.

- **Title Readability:**

  - **Reasoning:** Event titles include codes and abbreviations, such as "IF:5:S1::Promo:EDT::5IF_S1_GR_CM #001" and "HU:0:S1::S-SERIE4:TD::SERIE4-OPT18 #001". These titles seem designed for internal use rather than for user-friendliness, making them difficult to understand without context. If I replace these codes with more descriptive names, it would improve readability for students.

  - **Conclusion:** The event titles are **not readable** and need simplification.

- **Course Units and Abbreviations:**

  - **Reasoning:** From the descriptions and patterns in the titles, I can identify certain recurring terms as abbreviations for course units. For example, "PSAT" likely stands for "Projet de Synthèse Scientifique et Technique", and "OT8" relates to "Text Mining" based on the description provided. Using the course codes consistently throughout the clusters, I can map these abbreviations to full course names without translating them.

  - **Conclusion:** Identified course units and abbreviations are:
    - **Promo**: "Promotion"
    - **PSAT**: "Projet de Synthèse Scientifique et Technique"
    - **OT8**: "Text Mining"
    - **EPS**: "Éducation Physique et Sportive"
    - **TCS1**: "Fondements scientifiques de l'informatique"
    - **TCS2**: "Modélisation et simulation de systèmes"
    - **SERIE4**: "Options Sciences Humaines et Sociales"
    - **MAN-HU**: "Management d'équipe"

- **Event Type Identification:**

  - **Reasoning:** It’s good to know what type of class (e.g., "CM", "TD") an event represents to provide more detailed information in the event title. The event types are embedded within descriptions, like ":CM:" for lectures and ":TD:" for tutorials. By extracting these types and adding them to the event titles, I can make the schedule more intuitive.

  - **Conclusion:** Event types can be identified using terms like ":CM:" and ":TD:" found in descriptions.

**2. Brainstorming Rules:**

- **Reasoning:** There are three major issues I need to address with these rules: unreadable titles, lack of color differentiation, and unclear event types. I should tackle these systematically:
  
  - **Simplifying Titles:** The event titles are cluttered with codes. By replacing cryptic course unit codes with their full names, I can make them more accessible. This replacement should maintain the original language since it’s a familiar context for the user.

  - **Assigning Colors:** Color coding helps students quickly identify different course units. I’ll prioritize assigning brighter colors to key courses related to the user's main field of study, like "TCS1", "TCS2", and "PSAT", which seem central to computer science studies. For general administrative events like "Promo", a neutral color like "graphite" is appropriate.

  - **Indicating Event Type:** Prepending event types (like "CM - " for lectures) makes it clear what kind of class an event represents. This helps students quickly grasp the nature of each event without delving into descriptions.

- **Conclusion:** 
  - **Problem 1: Unreadable Titles**
    - **Conditions**: If the title contains specific course unit codes (e.g., "PSAT", "OT8", "EPS", "TCS1", "TCS2", "SERIE4", "MAN-HU", "Promo").
    - **Actions**: Change the title to the full course name.

  - **Problem 2: Lack of Color Differentiation**
    - **Conditions**: Same as above for each course unit.
    - **Actions**: Assign a unique color to each course unit.

  - **Problem 3: Unclear Event Types in Titles**
    - **Conditions**: If the description contains ":CM:", ":TD:", etc.
    - **Actions**: Prepend the event type abbreviation (e.g., "CM - ", "TD - ") to the title.

- **Color Assignments:**
  - **Reasoning:** The time schedule indicates a focus on computer science courses, so I will use more prominent colors for "TCS1" and "TCS2". These courses fall under a broader "formation par la recherche" theme, so both will use the "flamingo" color to reflect their connection. Courses like "OT8" deserve a distinct color ("tomato") to highlight their specificity, while non-academic activities like "Promo" can remain grey ("graphite").

  - **Conclusion:** Color assignments will be:
    - **PSAT**: "banana"
    - **TCS1** and **TCS2**: "flamingo"
    - **OT8**: "tomato"
    - **EPS**: "tangerine"
    - **SERIE4**: "peacock"
    - **MAN-HU**: "sage"
    - **Promo**: "graphite"
""",
    ruleset=Ruleset.model_validate_json(
        """{
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
          "value": "Éducation Physique et Sportive"
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
"""
    ),
)
