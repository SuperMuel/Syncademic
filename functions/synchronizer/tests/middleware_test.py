import arrow

from synchronizer.event import Event
from synchronizer.middleware.insa_middleware import prettify_title


class TestInsaMiddleware:
    def test_prettify_title(self):
        before = Event(
            title="IF:4:S2::PLD-COMP:CM::IF-4-S2-GR-CM #001",
            description="\n[IF-4-S2-EC-PLD-COMP:CM] Projet compilateur\n(Amphi BMC)\n\nIF:4:S2::PLD-COMP:CM::IF-4-S2-GR-CM\nGUERIN Eric\n\n(Exporté le:14/03/2 024 11:50)\n\n",
            start=arrow.get("2023-01-01T09:00:00"),
            end=arrow.get("2023-01-01T10:00:00"),
        )

        after = prettify_title(before)

        assert after.title == "Projet compilateur"

    def test_prettify_title_but_there_is_no_pretty_title_in_description(self):
        before = Event(
            title="IF:4:S2::PLD-COMP:CM::IF-4-S2-GR-CM #001",
            description="\n[IF-4-S2-EC-PLD-COMP:CM]\n(Amphi BMC)\n\nIF:4:S2::PLD-COMP:CM::IF-4-S2-GR-CM\nGUERIN Eric\n\n(Exporté le:14/03/2 024 11:50)\n\n",
            start=arrow.get("2023-01-01T09:00:00"),
            end=arrow.get("2023-01-01T10:00:00"),
        )

        after = prettify_title(before)

        assert after.title == before.title  # Title should not change

    def test_prettify_title_with_newlines(self):
        before = Event(
            title="IF:4:S2::PLD-COMP:CM::IF-4-S2-GR-CM #001",
            description="\n[IF-4-S2-EC-PLD-COMP:CM] Projet compilateur\n\n\n\n(Amphi BMC)\n\nIF:4:S2::PLD-COMP:CM::IF-4-S2-GR-CM\nGUERIN Eric\n\n(Exporté le:14/03/2 024 11:50)\n\n",
            start=arrow.get("2023-01-01T09:00:00"),
            end=arrow.get("2023-01-01T10:00:00"),
        )
        after = prettify_title(before)

        assert after.title, "Projet compilateur"
