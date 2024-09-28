from typing import List
from ..event import Event, GoogleEventColor
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


def CM_TD_TP_Middleware(events: List[Event]) -> List[Event]:
    def _edit_title(event: Event) -> Event:
        if ":CM" in event.description:
            return replace(event, title=f"CM - {event.title}")
        elif ":TD" in event.description:
            return replace(event, title=f"TD - {event.title}")
        elif ":TP" in event.description:
            return replace(event, title=f"TP - {event.title}")
        return event

    return [_edit_title(event) for event in events]


def Insa5IFMiddleware(events: List[Event]) -> List[Event]:
    # if we are not in INSA 5IF, we don't apply the middleware
    # If "IF-5" is not in more than 50% of the descriptions, we don't apply the middleware
    in_5if_events_count = sum(["IF-5" in event.description for event in events])
    if in_5if_events_count / len(events) < 0.5:
        return events

    def _edit_color(event: Event) -> Event:
        COLORS_MAP = {
            "EPS": GoogleEventColor.FLAMINGO,
            # Formation par la Recherche : Fondements scientifiques de l'informatique
            "EC-TCS1": GoogleEventColor.TANGERINE,
            # Formation par la Recherche : Modélisation et simulation de systèmes
            "EC-TCS2": GoogleEventColor.TANGERINE,
            # Projet de Synthèse Scientifique et Technique
            "EC-PSAT": GoogleEventColor.BANANA,
            # OT période 1
            ### OT5 : Calcul parallèle et GPU
            "EC-OT5": GoogleEventColor.TOMATO,
            ### OT7: Data Engineering
            "EC-OT7": GoogleEventColor.TOMATO,
            ### OT8: Text Mining - NLP
            "EC-OT8": GoogleEventColor.TOMATO,
            # OT période 2
            ### OT2: Big Data Analytics
            "EC-OT2": GoogleEventColor.TOMATO,
            ### OT3:Vie Privée
            "EC-OT3": GoogleEventColor.TOMATO,
            ### OT9: Cybersécurité
            "EC-OT9": GoogleEventColor.TOMATO,
            # Créneau Promo
            "Promo:EDT": GoogleEventColor.GRAPHITE,
            # Management d'équipe
            "EC-MAN": GoogleEventColor.SAGE,
        }
        for key, value in COLORS_MAP.items():
            if key in event.description:
                return replace(event, color=value)

        return event

    def _edit_title(event: Event) -> Event:
        if "Séminaire Entreprises" in event.description:
            return replace(event, title="Séminaire Entreprises")

        if "Matinée Thématique" in event.description:
            return replace(event, title="Matinée Thématique")

        if "Fondements scientifiques de l'informatique" in event.description:
            return replace(event, title="Fondements scientifiques de l'informatique")

        if "Modélisation et simulation de systèmes" in event.description:
            return replace(event, title="Modélisation et simulation de systèmes")

        return event

    new_events = []

    for event in events:
        new_event = _edit_color(event)
        new_event = _edit_title(new_event)
        new_events.append(new_event)

    return new_events
