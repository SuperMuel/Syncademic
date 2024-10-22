from functions.ai.types import RulesetOutput
from functions.rules.models import Ruleset


SYSTEM_PROMPT = """Create customization rules in JSON format for personalizing university schedule synchronization with Google Calendar. Use the provided compressed view of the time schedule to generate these rules.

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
"""

EXAMPLE_COMPRESSION_1 = """Cluster 2 (46 events):
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
"""


EXAMPLE_OUTPUT_1 = RulesetOutput(
    brainstorming="""1. Analyze the time schedule
   - What's the time schedule base language?
     - The base language of the time schedule is French, as seen in terms like "Créneau", "Réunion présentation", and "Formation par la Recherche".
   
   - Are the titles readable?
     - The titles are not very readable as they contain a lot of abbreviations and codes, such as "IF:5:S1::Promo:EDT::5IF_S1_GR_CM". These could be simplified for better readability.

   - What are the different course units, and their eventual abbreviations ? Do not translate the names.
     - CM: Cours Magistral (Well known in France)
     - TD: Travaux Dirigés (Well known in France)
     - TP: Travaux Pratiques (Well known in France)
     - IF: Informatique
     - S1: Semester 1
     - Promo: Promotion
     - EDT: Emploi du Temps
     - PSAT: Projet de Synthèse Scientifique et Technique
     - OT8: Text mining
     - EPS: Education Physique et Sportive
     - TCS1: Fondements scientifiques de l'informatique
     - TCS2: Modélisation et simulation de systèmes
     - SERIE4: Options Sciences Humaines et Sociales
     - MAN-HU: Management d'équipe

   - Do the title or description contain what kind of event this is?
     - Yes, the descriptions often contain the type of event, such as "CM" for Cours Magistral (Lecture) and "TD" for Travaux Dirigés (Tutorial).


2. Brainstorm the rules you plan to write. Identify the conditions and the actions to solve the titles and colors problems.

### Problems to solve
The problems to solve are : 
1. Simplifying the event titles by replacing the cryptic codes with readable names
2. Assigning distinct colors to different course units and 
3. Indicating in the title whether the event is a "CM" or a "TD". 

### How the rules can solve these problems
Since the rules are applied sequentially, I can first create rules for the rules 1. and 2., and then create the last rules that prepend to the title the type of event. 


   - Conditions:
     - If the title contains specific course unit codes like "Promo", "PSAT", "OT8", "EPS", "TCS1", "TCS2", "SERIE4", "MAN-HU". I will use case-sensitive to avoid matching mistakes. 
   
   - Actions:
     - Simplify event titles by replacing codes with more readable names, while keeping the original language.
       - "Promo" -> "Promo" (This is already readable)
       - "PSAT" -> "Projet de Synthèse Scientifique et Technique"
       - "OT8" -> "Text Mining"
       - "EPS" -> "Education Physique et Sportive"
       - "TCS1" -> "Fondements scientifiques de l'informatique"
       - "TCS2" -> "Modélisation et simulation de systèmes"
       - "SERIE4" -> "Options Sciences Humaines et Sociales"
       - "MAN-HU" -> "Management d'équipe"
     - Assign distinct colors to course units:
       Since the time schedule seems to be focused on computer science, I will apply strongest colors to computer science related course units.  TSC1 and TSC2 are related to the same domain "formation par la recherche" so I will apply the same color. 
       - "Promo" : Since it seems to be a placeholder, I will apply a grey color "graphite".
       - "PSAT" -> "banana" 
       - "TSC1" -> "flamingo"
       - "TSC2" -> "flamingo"
       - "OT8" -> "tomato"
       - "EPS" -> "tangerine"
       - "SERIE4" -> "peacock"
       - "MAN-HU" -> "sage"
  
Lastly, to indicate in the title whether an event is a "CM" or a "TD", I can use a rule that prepends `CM - ` `TD - ` to the title, when `:CM:` or `:TD:` is in the event's description, case-sensitive.
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
"""
    ),
)
