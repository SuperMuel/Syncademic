from typing import Sequence

from firebase_functions import logger
from langchain.chat_models import init_chat_model

from functions.ai.ruleset_builder import RulesetBuilder
from functions.ai.time_schedule_compressor import TimeScheduleCompressor
from functions.models.rules import Ruleset
from functions.models.sync_profile import SyncProfile
from functions.repositories.sync_profile_repository import (
    ISyncProfileRepository,
)
from functions.services.exceptions.ruleset import RulesetGenerationError
from functions.services.ics_service import IcsService
from functions.synchronizer.ics_parser import IcsParser
from functions.synchronizer.ics_source import UrlIcsSource


class AiRulesetService:
    """Service for generating AI-powered rulesets for calendar customization.

    This service handles the creation of customized rulesets for sync profiles by:
    1. Fetching and parsing ICS calendar data
    2. Compressing the schedule to reduce redundancy
    3. Using AI to generate appropriate customization rules
    4. Storing the resulting ruleset in the repository

    The service uses a combination of ICS parsing, schedule compression, and AI models
    to automatically generate rules that improve calendar readability and usability.

    Attributes:
        ics_service: Service for fetching and parsing ICS calendar data
        sync_profile_repo: Repository for storing sync profile data
        ruleset_builder: Component for generating rulesets using AI
    """

    def __init__(
        self,
        ics_service: IcsService,
        sync_profile_repo: ISyncProfileRepository,
        ruleset_builder: RulesetBuilder,
    ):
        self.ics_service = ics_service
        self.sync_profile_repo = sync_profile_repo
        self.ruleset_builder = ruleset_builder

    def create_ruleset_for_sync_profile(
        self,
        sync_profile: SyncProfile,
    ) -> None:
        """Creates or updates an AI-generated ruleset for a sync profile.

        This method fetches and parses the ICS calendar data from the sync profile's schedule source,
        compresses the schedule to reduce redundancy, generates an AI ruleset based on the events,
        and stores the result in the sync profile repository.

        Args:
            sync_profile: The sync profile containing the schedule source and user information.

        Raises:
            None: Errors are handled internally and stored in the sync profile repository.

        Note:
            If any errors occur during fetching, parsing, or ruleset generation,
            they are logged and stored in the sync profile repository rather than raised.
        """

        events_or_error, ics_str = self.ics_service.try_fetch_and_parse_with_ics_str(
            ics_source=sync_profile.scheduleSource.to_ics_source(),
            save_to_storage=True,
            metadata={
                "sync_profile_id": sync_profile.id,
                "user_id": sync_profile.user_id,
            },
        )

        if isinstance(events_or_error, Exception):
            return self.sync_profile_repo.update_ruleset_error(
                user_id=sync_profile.user_id,
                sync_profile_id=sync_profile.id,
                error_str=f"Failed to fetch and parse ICS: {str(events_or_error)}",
            )

        events = events_or_error
        assert ics_str is not None

        try:
            # Generate ruleset
            output = self.ruleset_builder.generate_ruleset(
                events,
                metadata={
                    "ics_url": sync_profile.scheduleSource.url,
                    "user_id": sync_profile.user_id,
                    "sync_profile_id": sync_profile.id,
                },
                original_ics_size_chars=len(ics_str),
            )
        except Exception as e:
            logger.error(f"Failed to generate ruleset: {e}")
            self.sync_profile_repo.update_ruleset_error(
                user_id=sync_profile.user_id,
                sync_profile_id=sync_profile.id,
                error_str=f"Failed to generate ruleset: {type(e).__name__}: {str(e)}",
            )
            return

        logger.info(f"Generated ruleset: {str(output.ruleset)[:100]}...")
        # Store ruleset
        self.sync_profile_repo.update_ruleset(
            user_id=sync_profile.user_id,
            sync_profile_id=sync_profile.id,
            ruleset=output.ruleset,
        )
