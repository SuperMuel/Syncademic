from datetime import datetime, timezone
from unittest.mock import Mock, create_autospec

import pytest
from arrow import Arrow
from pydantic import HttpUrl
from pytest_mock import MockFixture

from functions.ai.ruleset_builder import RulesetBuilder
from functions.models.sync_profile import (
    ScheduleSource,
    SyncProfile,
    SyncProfileStatus,
    SyncProfileStatusType,
    SyncTrigger,
    SyncType,
    TargetCalendar,
)
from functions.repositories.sync_profile_repository import (
    ISyncProfileRepository,
    MockSyncProfileRepository,
)
from functions.services.ai_ruleset_service import AiRulesetService
from functions.services.ics_service import IcsService
from functions.shared.event import Event
from tests.util import VALID_RULESET


@pytest.fixture
def mock_ics_service() -> Mock:
    return create_autospec(IcsService)


@pytest.fixture
def mock_sync_profile_repo() -> ISyncProfileRepository:
    return MockSyncProfileRepository()


@pytest.fixture
def mock_ruleset_builder() -> Mock:
    return create_autospec(RulesetBuilder)


@pytest.fixture
def service(
    mock_ics_service: Mock,
    mock_sync_profile_repo: ISyncProfileRepository,
    mock_ruleset_builder: Mock,
) -> AiRulesetService:
    return AiRulesetService(
        ics_service=mock_ics_service,
        sync_profile_repo=mock_sync_profile_repo,
        ruleset_builder=mock_ruleset_builder,
    )


@pytest.fixture
def sample_sync_profile() -> SyncProfile:
    return SyncProfile(
        id="test-profile-id",
        user_id="test-user-id",
        title="test-title",
        targetCalendar=TargetCalendar(
            id="test-target-calendar-id",
            title="test-target-calendar-title",
            description="test-target-calendar-description",
            providerAccountId="test-provider-account-id",
            providerAccountEmail="info@example.com",
        ),
        status=SyncProfileStatus(
            type=SyncProfileStatusType.NOT_STARTED,
            syncTrigger=SyncTrigger.ON_CREATE,
            syncType=SyncType.REGULAR,
        ),
        scheduleSource=ScheduleSource(url=HttpUrl("https://example.com/calendar.ics")),
    )


@pytest.fixture
def sample_events() -> list[Event]:
    return [
        Event(
            title="Test Event 1",
            description="Description 1",
            start=Arrow.fromdatetime(datetime(2024, 1, 1, 9, 0, 0), timezone.utc),
            end=Arrow.fromdatetime(datetime(2024, 1, 1, 10, 0, 0), timezone.utc),
        ),
        Event(
            title="Test Event 2",
            description="Description 2",
            start=Arrow.fromdatetime(datetime(2024, 1, 1, 11, 0, 0), timezone.utc),
            end=Arrow.fromdatetime(datetime(2024, 1, 1, 12, 0, 0), timezone.utc),
        ),
    ]


class TestAiRulesetService:
    def test_successful_ruleset_creation(
        self,
        service: AiRulesetService,
        mock_ics_service: Mock,
        mock_sync_profile_repo: MockSyncProfileRepository,
        mock_ruleset_builder: Mock,
        sample_sync_profile: SyncProfile,
        sample_events: list[Event],
    ) -> None:
        """Test successful creation and storage of a ruleset."""
        # Arrange
        mock_sync_profile_repo.save_sync_profile(sample_sync_profile)
        mock_ics_service.try_fetch_and_parse_with_ics_str.return_value = (
            sample_events,
            "ics_str",
        )
        mock_ruleset_builder.generate_ruleset.return_value = Mock(ruleset=VALID_RULESET)

        # Act
        service.create_ruleset_for_sync_profile(sample_sync_profile)

        # Assert
        sync_profile = mock_sync_profile_repo.get_sync_profile(
            user_id=sample_sync_profile.user_id,
            sync_profile_id=sample_sync_profile.id,
        )
        assert sync_profile is not None
        assert sync_profile.ruleset == VALID_RULESET

    def test_handles_ics_fetch_error(
        self,
        service: AiRulesetService,
        mock_ics_service: Mock,
        mock_sync_profile_repo: MockSyncProfileRepository,
        mock_ruleset_builder: Mock,
        sample_sync_profile: SyncProfile,
    ) -> None:
        """Test handling of ICS fetch errors."""
        # Arrange
        error = Exception("Failed to fetch ICS")
        mock_ics_service.try_fetch_and_parse_with_ics_str.return_value = (
            error,
            None,
        )
        mock_sync_profile_repo.save_sync_profile(sample_sync_profile)

        # Act
        service.create_ruleset_for_sync_profile(sample_sync_profile)

        # Assert

        sync_profile = mock_sync_profile_repo.get_sync_profile(
            user_id=sample_sync_profile.user_id,
            sync_profile_id=sample_sync_profile.id,
        )
        assert sync_profile is not None
        assert (
            sync_profile.ruleset_error
            == "Failed to fetch and parse ICS: Failed to fetch ICS"
        )
        mock_ruleset_builder.generate_ruleset.assert_not_called()

    def test_handles_ruleset_generation_error(
        self,
        service: AiRulesetService,
        mock_ics_service: Mock,
        mock_sync_profile_repo: MockSyncProfileRepository,
        mock_ruleset_builder: Mock,
        sample_sync_profile: SyncProfile,
        sample_events: list[Event],
    ) -> None:
        """Test handling of ruleset generation errors."""
        # Arrange
        mock_ics_service.try_fetch_and_parse_with_ics_str.return_value = (
            sample_events,
            "ics_str",
        )
        mock_ruleset_builder.generate_ruleset.side_effect = Exception(
            "Failed to generate ruleset"
        )
        mock_sync_profile_repo.save_sync_profile(sample_sync_profile)
        # Act
        service.create_ruleset_for_sync_profile(sample_sync_profile)

        # Assert
        sync_profile = mock_sync_profile_repo.get_sync_profile(
            user_id=sample_sync_profile.user_id,
            sync_profile_id=sample_sync_profile.id,
        )
        assert sync_profile is not None
        assert (
            sync_profile.ruleset_error
            == "Failed to generate ruleset: Exception: Failed to generate ruleset"
        )
