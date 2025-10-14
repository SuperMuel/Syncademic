import logging
import traceback

from backend.ai.ruleset_builder import RulesetBuilder
from backend.infrastructure.event_bus import IEventBus
from backend.models.sync_profile import SyncProfile
from backend.repositories.sync_profile_repository import (
    ISyncProfileRepository,
)
from backend.services.exceptions.ics import BaseIcsError
from backend.services.ics_service import IcsService
from backend.shared.domain_events import RulesetGenerationFailed

logger = logging.getLogger(__name__)


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
        event_bus: IEventBus,
    ):
        self.ics_service = ics_service
        self.sync_profile_repo = sync_profile_repo
        self.ruleset_builder = ruleset_builder
        self.event_bus = event_bus

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
        logger.info(
            "Creating ruleset for sync profile %s",
            sync_profile.id,
            extra={
                "sync_profile_id": sync_profile.id,
                "user_id": sync_profile.user_id,
            },
        )

        result_or_error = self.ics_service.try_fetch_and_parse(
            ics_source=sync_profile.scheduleSource.to_ics_source(),
            metadata={
                "sync_profile_id": sync_profile.id,
                "user_id": sync_profile.user_id,
                "source": sync_profile.scheduleSource.model_dump(),
                "purpose": "create_ruleset",
            },
        )

        if isinstance(result_or_error, BaseIcsError):
            sync_profile.update_ruleset(
                error=f"Failed to fetch and parse ICS: {str(result_or_error)}"
            )
            self.sync_profile_repo.save_sync_profile(sync_profile)
            self.event_bus.publish(
                RulesetGenerationFailed(
                    user_id=sync_profile.user_id,
                    sync_profile_id=sync_profile.id,
                    error_type=type(result_or_error).__name__,
                    error_message=str(result_or_error),
                    formatted_traceback=traceback.format_exc(),
                )
            )
            return

        events, ics_str = result_or_error.events, result_or_error.raw_ics

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
            logger.error("Failed to generate ruleset: %s", e)
            sync_profile.update_ruleset(
                error=f"Failed to generate ruleset: {type(e).__name__}: {str(e)}"
            )
            self.sync_profile_repo.save_sync_profile(sync_profile)
            self.event_bus.publish(
                RulesetGenerationFailed(
                    user_id=sync_profile.user_id,
                    sync_profile_id=sync_profile.id,
                    error_type=type(e).__name__,
                    error_message=str(e),
                    formatted_traceback=traceback.format_exc(),
                )
            )
            return

        logger.info("Generated ruleset: %s", str(output.ruleset)[:100] + "...")

        # Store ruleset
        sync_profile.update_ruleset(ruleset=output.ruleset)
        self.sync_profile_repo.save_sync_profile(sync_profile)
