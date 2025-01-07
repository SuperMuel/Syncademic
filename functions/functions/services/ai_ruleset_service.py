from functions.models.rules import Ruleset
from functions.models.sync_profile import SyncProfile


class AiRulesetService:
    def generate_ruleset_for_sync_profile(self, sync_profile: SyncProfile) -> Ruleset:
        """
        1) Fetch ICS events (possibly delegating to IcsService).
        2) Compress them.
        3) Use the LLM to create a Ruleset.
        4) Return the ruleset.
        """

    def store_ruleset(
        self,
        user_id: str,
        sync_profile_id: str,
        ruleset: Ruleset,
    ) -> None:
        """
        Stores the generated Ruleset in Firestore, attached to the sync profile.
        """
