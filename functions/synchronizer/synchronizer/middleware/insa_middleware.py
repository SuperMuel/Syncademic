from typing import List
from ..event import Event
import re
from dataclasses import replace


def TitlePrettifier(events: List[Event]) -> List[Event]:
    return [prettify_title(event) for event in events]


def prettify_title(event: Event) -> Event:
    r"""
    
    At INSA, the title of an event is not always the name of the course. It can be a code like "IF:4:S2::PLD-COMP:CM::IF-4-S2-GR-CM #001".

    However, in the description, there is the name of the course. This function takes the name of the course in the description and put it in the title.

    Example:

    Here is an example of a description
    ```
    \n[IF-4-S2-EC-PLD-COMP:CM] Projet compilateur\n(Amphi BMC)\n\
 nIF:4:S2::PLD-COMP:CM::IF-4-S2-GR-CM\nGUERIN Eric\n\n(Exporté le:14/03/2
 024 11:50)\n\n
    ```

    The title is "IF:4:S2::PLD-COMP:CM::IF-4-S2-GR-CM #001" and the name of the course is "Projet compilateur".

    This function will change the title to "Projet compilateur".

    If there is no name of the course in the description, the title will not change.
    """

    description = event.description

    # the name of the course is between the first "]" and the first "\n"
    # example: "[IF-4-S2-EC-PLD-COMP:CM] Projet compilateur\n(Amphi BMC)\n\nIF:4:S2::PLD-COMP:CM::IF-4-S2-GR-CM\nGUERIN Eric\n\n(Exporté le:14/03/2 024 11:50)\n\n"
    # the name of the course is "Projet compilateur"
    match = re.search(r"\](.*)\n", description)

    if match is None or match.group(1).strip() == "":
        return event

    pretty_title = match.group(1).strip()
    return replace(event, title=pretty_title)


# TODO : maybe show if that's a CM, or TD, or TP


def ExamPrettifier(events: List[Event]) -> List[Event]:
    return [_add_exam_emoji(event) for event in events]


def _add_exam_emoji(event: Event) -> Event:
    r"""
    SUMMARY:IF:4:S2::AFQL:EV::IF-4-S2-GR-CM
    LOCATION:501.212 - TD 212\,501.329 - TD 329\,501.331 - TD 331\,5020002 -
    Pierre-Gilles de Gennes
    DESCRIPTION:\n[IF-4-S2-EC-AFQL:EV] Approche Formelle pour la Qualité Logi
    ciel\n()\n\nIF:4:S2::AFQL:EV::IF-4-S2-GR-CM\n\n(Exporté le:14/03/2024 13
    :44)\n\n
    """

    if ":EV]" in event.description:
        return replace(event, title=f"🚨 {event.title}")

    return event
