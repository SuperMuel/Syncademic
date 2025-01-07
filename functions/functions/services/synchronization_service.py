from functions.models.sync_profile import SyncTrigger, SyncType


class SynchronizationService:
    def synchronize(
        self,
        user_id: str,
        sync_profile_id: str,
        sync_trigger: SyncTrigger,
        sync_type: SyncType = SyncType.REGULAR,
    ) -> None:
        """
        Orchestrates:
        1) Fetching the SyncProfile.
        2) Checking if it's in a valid state to sync.
        3) Checking usage limits.
        4) Fetching/parsing ICS events.
        5) Applying AI rules (if available).
        6) Deleting stale events and inserting the new ones in the target calendar.
        7) Updating SyncProfile status and usage stats.
        """

    # def perform_synchronization(
    #     self,
    #     sync_profile_id: str,
    #     sync_trigger: SyncTrigger,
    #     ics_str: str,
    #     ruleset: Ruleset | None,
    #     sync_type: SyncType = SyncType.REGULAR,
    # ) -> None:
    #     """
    #     Lower-level “do the actual event creation/deletion” step—assuming
    #     you’ve already fetched and parsed the ICS string. This is effectively
    #     what’s currently inside the old `perform_synchronization` function.
    #     """
