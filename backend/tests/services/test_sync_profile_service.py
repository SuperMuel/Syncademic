from pydantic import HttpUrl
import pytest
import arrow
from unittest.mock import Mock

from backend.infrastructure.event_bus import MockEventBus
from backend.models.sync_profile import (
    SyncProfile,
    SyncProfileStatus,
    SyncProfileStatusType,
    SyncTrigger,
    SyncType,
    ScheduleSource,
    TargetCalendar,
)
from backend.services.ai_ruleset_service import AiRulesetService
from backend.services.exceptions.sync import DailySyncLimitExceededError
from backend.services.google_calendar_service import GoogleCalendarService
from backend.shared import domain_events
from backend.shared.event import Event
from backend.shared.google_calendar_colors import GoogleEventColor
from backend.services.sync_profile_service import SyncProfileService
from backend.services.exceptions.ics import (
    IcsParsingError,
    IcsSourceError,
)
from backend.services.ics_service import IcsFetchAndParseResult
from backend.repositories.sync_stats_repository import MockSyncStatsRepository
from backend.repositories.sync_profile_repository import MockSyncProfileRepository
from backend.synchronizer.google_calendar_manager import MockGoogleCalendarManager
from backend.models.schemas import (
    CreateSyncProfileInput,
    CreateNewTargetCalendarInput,
    UseExistingTargetCalendarInput,
)
from backend.services.exceptions.target_calendar import TargetCalendarNotFoundError


def _make_sync_profile(
    user_id: str = "user123",
    sync_profile_id: str = "profileABC",
    status_type: SyncProfileStatusType = SyncProfileStatusType.SUCCESS,
    ruleset=None,
) -> SyncProfile:
    """Helper to create a minimal SyncProfile object."""
    return SyncProfile(
        id=sync_profile_id,
        user_id=user_id,
        title="Test Profile",
        scheduleSource=ScheduleSource(url=HttpUrl("https://example.com/calendar.ics")),
        targetCalendar=TargetCalendar(
            id="calendar123",
            title="MyCalendar",
            description="",
            providerAccountId="googleUser123",
            providerAccountEmail="test@example.com",
        ),
        status=SyncProfileStatus(type=status_type),
        ruleset=ruleset,
    )


@pytest.fixture
def sync_profile_repo() -> MockSyncProfileRepository:
    """
    Real in-memory SyncProfileRepository so we can store/fetch profiles
    without mocking every method call.
    """
    return MockSyncProfileRepository()


@pytest.fixture
def auth_service_mock():
    """
    Mock of AuthorizationService. We'll stub get_authenticated_google_calendar_manager(...)
    to return a MockGoogleCalendarManager.
    """
    return Mock()


@pytest.fixture
def ics_service_mock():
    """
    Mock of IcsService.
    We'll control the return value of try_fetch_and_parse(...) (IcsFetchAndParseResult or a BaseIcsError).
    """
    return Mock()


@pytest.fixture
def sync_stats_repo() -> MockSyncStatsRepository:
    """Real in-memory stats repo to verify daily increments."""
    return MockSyncStatsRepository()


@pytest.fixture
def mock_event_bus() -> MockEventBus:
    return MockEventBus()


@pytest.fixture
def google_calendar_service() -> GoogleCalendarService:
    return Mock()


@pytest.fixture
def ai_ruleset_service() -> AiRulesetService:
    return Mock()


@pytest.fixture
def sync_profile_service(
    sync_profile_repo,
    sync_stats_repo,
    auth_service_mock,
    ics_service_mock,
    mock_event_bus,
    google_calendar_service,
    ai_ruleset_service,
):
    """Create a SyncProfileService with the real MockSyncProfileRepository."""
    return SyncProfileService(
        sync_profile_repo=sync_profile_repo,
        sync_stats_repo=sync_stats_repo,
        authorization_service=auth_service_mock,
        ics_service=ics_service_mock,
        event_bus=mock_event_bus,
        google_calendar_service=google_calendar_service,
        ai_ruleset_service=ai_ruleset_service,
    )


@pytest.fixture
def future_event() -> Event:
    now = arrow.now()
    return Event(
        start=now.shift(hours=+1),
        end=now.shift(hours=+2),
        title="Future Event",
    )


@pytest.fixture
def past_event() -> Event:
    now = arrow.now()
    return Event(
        start=now.shift(hours=-2),
        end=now.shift(hours=-1),
        title="Past Event",
    )


@pytest.fixture
def past_all_day_event() -> Event:
    today = arrow.now().shift(days=-1).floor("day")
    return Event(
        start=today,
        end=today.shift(days=1),
        title="Past All Day",
        is_all_day=True,
    )


def test_on_create_success(
    sync_profile_service,
    sync_profile_repo,
    auth_service_mock,
    ics_service_mock,
    future_event,
    past_event,
    mock_event_bus,
):
    """
    ON_CREATE scenario: ICS returns 2 events, both get created.
    We store the profile in memory with status=NOT_STARTED,
    then check final status in the repo after sync.
    """
    user_id = "user123"
    prof_id = "profile_on_create"

    # ICS returns 2 events
    ics_service_mock.try_fetch_and_parse.return_value = IcsFetchAndParseResult(
        events=[past_event, future_event],
        raw_ics="mock irrelevant ics value",
    )

    # Put a NOT_STARTED profile into the repository
    profile = _make_sync_profile(
        user_id=user_id,
        sync_profile_id=prof_id,
        status_type=SyncProfileStatusType.NOT_STARTED,
    )
    sync_profile_repo.save_sync_profile(profile)

    # Provide a mock manager
    manager = MockGoogleCalendarManager()
    auth_service_mock.get_authenticated_google_calendar_manager.return_value = manager

    # Act
    sync_profile_service.synchronize(
        user_id=user_id,
        sync_profile_id=prof_id,
        sync_trigger=SyncTrigger.ON_CREATE,
        sync_type=SyncType.REGULAR,
    )

    # ICS was called
    ics_service_mock.try_fetch_and_parse.assert_called_once()

    # 2 events created
    all_events = manager.get_all_events(sync_profile_id=prof_id)
    assert len(all_events) == 2

    # final status = SUCCESS
    updated_profile = sync_profile_repo.get_sync_profile(user_id, prof_id)
    assert updated_profile is not None
    assert updated_profile.status.type == SyncProfileStatusType.SUCCESS

    mock_event_bus.assert_event_published_with_data(
        domain_events.SyncSucceeded,
        user_id=user_id,
        sync_profile_id=prof_id,
    )


def test_regular_sync_only_future(
    sync_profile_service,
    sync_profile_repo,
    auth_service_mock,
    ics_service_mock,
    future_event,
    past_event,
    mock_event_bus,
):
    """
    REGULAR sync scenario: ICS returns 1 past + 1 future event.
    Sync should only create the future event, and delete old future events.
    """
    user_id = "user123"
    prof_id = "profile_reg"

    ics_service_mock.try_fetch_and_parse.return_value = IcsFetchAndParseResult(
        events=[past_event, future_event],
        raw_ics="mock irrelevant ics value",
    )

    # Put a profile in SUCCESS state
    profile = _make_sync_profile(
        user_id=user_id,
        sync_profile_id=prof_id,
        status_type=SyncProfileStatusType.SUCCESS,
    )
    sync_profile_repo.save_sync_profile(profile)

    manager = MockGoogleCalendarManager()
    manager.create_events(
        [
            Event(start=future_event.start, end=future_event.end, title="Old Future1"),
            Event(start=future_event.start, end=future_event.end, title="Old Future2"),
        ],
        sync_profile_id=prof_id,
    )
    auth_service_mock.get_authenticated_google_calendar_manager.return_value = manager

    # Act
    sync_profile_service.synchronize(
        user_id=user_id,
        sync_profile_id=prof_id,
        sync_trigger=SyncTrigger.MANUAL,
        sync_type=SyncType.REGULAR,
    )

    # Only 1 new future event remains
    all_after = manager.get_all_events(sync_profile_id=prof_id)
    assert len(all_after) == 1
    assert all_after[0]["summary"] == "Future Event"

    # final status => SUCCESS in the repository
    updated_profile = sync_profile_repo.get_sync_profile(user_id, prof_id)
    assert updated_profile is not None
    assert updated_profile.status.type == SyncProfileStatusType.SUCCESS

    mock_event_bus.assert_event_published_with_data(
        domain_events.SyncSucceeded,
        user_id=user_id,
        sync_profile_id=prof_id,
    )


def test_regular_sync_handles_past_all_day_event(
    sync_profile_service,
    sync_profile_repo,
    auth_service_mock,
    ics_service_mock,
    future_event,
    past_all_day_event,
    mock_event_bus,
):
    """REGULAR sync should ignore past all-day events when deleting."""
    user_id = "user123"
    prof_id = "profile_all_day"

    ics_service_mock.try_fetch_and_parse.return_value = IcsFetchAndParseResult(
        events=[future_event],
        raw_ics="mock irrelevant ics value",
    )

    profile = _make_sync_profile(
        user_id=user_id,
        sync_profile_id=prof_id,
        status_type=SyncProfileStatusType.SUCCESS,
    )
    sync_profile_repo.save_sync_profile(profile)

    manager = MockGoogleCalendarManager()
    manager.create_events(
        [
            past_all_day_event,
            Event(start=future_event.start, end=future_event.end, title="Old Future"),
        ],
        sync_profile_id=prof_id,
    )
    auth_service_mock.get_authenticated_google_calendar_manager.return_value = manager

    sync_profile_service.synchronize(
        user_id=user_id,
        sync_profile_id=prof_id,
        sync_trigger=SyncTrigger.MANUAL,
        sync_type=SyncType.REGULAR,
    )

    all_after = manager.get_all_events(sync_profile_id=prof_id)
    summaries = sorted(event["summary"] for event in all_after)
    assert summaries == ["Future Event", "Past All Day"]

    updated_profile = sync_profile_repo.get_sync_profile(user_id, prof_id)
    assert updated_profile is not None
    assert updated_profile.status.type == SyncProfileStatusType.SUCCESS

    mock_event_bus.assert_event_published_with_data(
        domain_events.SyncSucceeded,
        user_id=user_id,
        sync_profile_id=prof_id,
    )


def test_full_sync_deletes_all(
    sync_profile_service,
    sync_profile_repo,
    auth_service_mock,
    ics_service_mock,
    past_event,
    future_event,
    mock_event_bus,
):
    """
    FULL sync: ICS returns 1 event, we remove all old events, create the new one.
    """
    user_id = "user123"
    prof_id = "profile_full"

    ics_service_mock.try_fetch_and_parse.return_value = IcsFetchAndParseResult(
        events=[future_event],
        raw_ics="mock irrelevant ics value",
    )

    profile = _make_sync_profile(
        user_id=user_id,
        sync_profile_id=prof_id,
        status_type=SyncProfileStatusType.SUCCESS,
    )
    sync_profile_repo.save_sync_profile(profile)

    manager = MockGoogleCalendarManager()
    manager.create_events(
        [
            # An event in the past. We want to assert that it gets deleted, that's
            # the difference between FULL and REGULAR syncs.
            Event(start=past_event.start, end=past_event.end, title="Old A"),
            # Some events in the future:
            Event(start=future_event.start, end=future_event.end, title="Old B"),
            Event(start=future_event.start, end=future_event.end, title="Old C"),
        ],
        sync_profile_id=prof_id,
    )
    auth_service_mock.get_authenticated_google_calendar_manager.return_value = manager

    sync_profile_service.synchronize(
        user_id=user_id,
        sync_profile_id=prof_id,
        sync_trigger=SyncTrigger.MANUAL,
        sync_type=SyncType.FULL,
    )

    # All old events removed, new event remains
    all_events = manager.get_all_events(sync_profile_id=prof_id)
    assert len(all_events) == 1
    assert all_events[0]["summary"] == "Future Event"

    updated_profile = sync_profile_repo.get_sync_profile(user_id, prof_id)
    assert updated_profile is not None
    assert updated_profile.status.type == SyncProfileStatusType.SUCCESS

    mock_event_bus.assert_event_published_with_data(
        domain_events.SyncSucceeded,
        user_id=user_id,
        sync_profile_id=prof_id,
    )


def test_ruleset_applied(
    sync_profile_service,
    sync_profile_repo,
    auth_service_mock,
    ics_service_mock,
    mock_event_bus,
):
    """
    ICS returns 1 event "Lecture", we have a ruleset that changes it to "Modified Lecture".
    Then we confirm the final status in the repository.
    """
    now = arrow.now()
    raw_event = Event(start=now, end=now.shift(hours=1), title="Lecture")
    ics_service_mock.try_fetch_and_parse.return_value = IcsFetchAndParseResult(
        events=[raw_event],
        raw_ics="mock irrelevant ics value",
    )

    from backend.models.rules import (
        Rule,
        Ruleset,
        TextFieldCondition,
        ChangeFieldAction,
    )

    cond = TextFieldCondition(field="title", operator="contains", value="Lecture")
    act = ChangeFieldAction(field="title", method="set", value="Modified Lecture")
    ruleset = Ruleset(rules=[Rule(condition=cond, actions=[act])])

    user_id = "user123"
    prof_id = "profileABC"
    profile = _make_sync_profile(ruleset=ruleset)
    sync_profile_repo.save_sync_profile(profile)

    manager = MockGoogleCalendarManager()
    auth_service_mock.get_authenticated_google_calendar_manager.return_value = manager

    sync_profile_service.synchronize(
        user_id=user_id,
        sync_profile_id=prof_id,
        sync_trigger=SyncTrigger.MANUAL,
        sync_type=SyncType.REGULAR,
    )

    # We should see 1 event with "Modified Lecture"
    all_events = manager.get_all_events(sync_profile_id=prof_id)
    assert len(all_events) == 1
    assert all_events[0]["summary"] == "Modified Lecture"

    # This is a temporary feature. We want all events to be grey by default, unless a rule
    # explicitly sets a color.
    assert all_events[0]["colorId"] == GoogleEventColor.GRAPHITE.to_color_id()

    updated_profile = sync_profile_repo.get_sync_profile(user_id, prof_id)
    assert updated_profile is not None
    assert updated_profile.status.type == SyncProfileStatusType.SUCCESS

    mock_event_bus.assert_event_published_with_data(
        domain_events.SyncSucceeded,
        user_id=user_id,
        sync_profile_id=prof_id,
    )


def test_fails_on_ics_fetch_error(
    sync_profile_service,
    sync_profile_repo,
    auth_service_mock,
    ics_service_mock,
    mock_event_bus,
):
    """
    ICS returns an IcsSourceError => final status=FAILED in repository, no events, usage=0.
    """
    user_id = "userXYZ"
    prof_id = "profileFail"

    error = IcsSourceError("Couldn't fetch")
    ics_service_mock.try_fetch_and_parse.return_value = error

    profile = _make_sync_profile(user_id=user_id, sync_profile_id=prof_id)
    sync_profile_repo.save_sync_profile(profile)

    manager = MockGoogleCalendarManager()
    auth_service_mock.get_authenticated_google_calendar_manager.return_value = manager

    sync_profile_service.synchronize(
        user_id=user_id,
        sync_profile_id=prof_id,
        sync_trigger=SyncTrigger.MANUAL,
        sync_type=SyncType.REGULAR,
    )

    updated_profile = sync_profile_repo.get_sync_profile(user_id, prof_id)
    assert updated_profile is not None
    assert updated_profile.status.type == SyncProfileStatusType.FAILED

    assert len(manager.get_all_events(sync_profile_id=prof_id)) == 0

    mock_event_bus.assert_event_published_with_data(
        domain_events.SyncFailed,
        user_id=user_id,
        sync_profile_id=prof_id,
        error_type=type(error).__name__,
        error_message=str(error),
    )

    assert (
        "most recent call last"
        in mock_event_bus.find_event(domain_events.SyncFailed).formatted_traceback
    )


def test_fails_on_ics_parse_error(
    sync_profile_service,
    sync_profile_repo,
    auth_service_mock,
    ics_service_mock,
    mock_event_bus,
):
    """
    ICS returns an IcsParseError => final status=FAILED in repository, no events, usage=0.
    """
    user_id = "userABC"
    prof_id = "profileParseError"

    # Simulate ICS parse error
    error = IcsParsingError("Failed to parse ICS")
    ics_service_mock.try_fetch_and_parse.return_value = error

    # Store initial profile
    profile = _make_sync_profile(user_id=user_id, sync_profile_id=prof_id)
    sync_profile_repo.save_sync_profile(profile)

    # Setup mock calendar manager
    manager = MockGoogleCalendarManager()
    auth_service_mock.get_authenticated_google_calendar_manager.return_value = manager

    # Act
    sync_profile_service.synchronize(
        user_id=user_id,
        sync_profile_id=prof_id,
        sync_trigger=SyncTrigger.MANUAL,
        sync_type=SyncType.REGULAR,
    )

    # Assert profile status is FAILED
    updated_profile = sync_profile_repo.get_sync_profile(user_id, prof_id)
    assert updated_profile is not None
    assert updated_profile.status.type == SyncProfileStatusType.FAILED

    # Assert no events were created
    assert len(manager.get_all_events(sync_profile_id=prof_id)) == 0

    # Assert sync failed event was published (which will not increment sync count)
    mock_event_bus.assert_event_published_with_data(
        domain_events.SyncFailed,
        user_id=user_id,
        sync_profile_id=prof_id,
    )


def test_raise_on_daily_limit(
    sync_profile_service,
    sync_profile_repo,
    auth_service_mock,
    ics_service_mock,
    sync_stats_repo,
    future_event,
    mock_event_bus,
):
    """
    If user exceeded daily limit, we fail early (status=FAILED in the repo),
    ICS not fetched, no events, usage doesn't increment.
    """
    # We'll saturate today's usage
    from backend.settings import settings

    user_id = "userX"
    prof_id = "profileLimit"

    for _ in range(settings.MAX_SYNCHRONIZATIONS_PER_DAY):
        sync_stats_repo.increment_sync_count(user_id)

    profile = _make_sync_profile(user_id=user_id, sync_profile_id=prof_id)
    sync_profile_repo.save_sync_profile(profile)

    manager = MockGoogleCalendarManager()
    auth_service_mock.get_authenticated_google_calendar_manager.return_value = manager

    with pytest.raises(DailySyncLimitExceededError):
        sync_profile_service.synchronize(
            user_id=user_id,
            sync_profile_id=prof_id,
            sync_trigger=SyncTrigger.MANUAL,
            sync_type=SyncType.REGULAR,
        )

    # Assert profile hasn't been touched
    assert sync_profile_repo.get_sync_profile(user_id, prof_id) == profile

    # ICS never called
    ics_service_mock.try_fetch_and_parse.assert_not_called()

    # No new events
    assert len(manager.get_all_events(sync_profile_id=prof_id)) == 0

    # Assert no SyncFailed event was published, because it's not
    # a failure of the sync itself, but a precondition failure.
    assert not mock_event_bus.find_event(domain_events.SyncFailed)


def test_successful_deletion(
    sync_profile_service: SyncProfileService, sync_profile_repo, auth_service_mock
):
    """Successful deletion flow with event cleanup"""
    user_id = "user123"
    prof_id = "profile123"

    # Setup profile with existing events
    profile = _make_sync_profile(
        user_id=user_id,
        sync_profile_id=prof_id,
        status_type=SyncProfileStatusType.SUCCESS,
    )
    sync_profile_repo.save_sync_profile(profile)

    # Mock calendar manager with existing events
    manager = MockGoogleCalendarManager()
    manager.create_events(
        [Event(start=arrow.now(), end=arrow.now().shift(hours=1), title="Test Event")],
        sync_profile_id=prof_id,
    )
    auth_service_mock.get_authenticated_google_calendar_manager.return_value = manager

    # Act
    sync_profile_service.delete_sync_profile(user_id, prof_id)

    # Assert
    assert sync_profile_repo.get_sync_profile(user_id, prof_id) is None
    assert len(manager.get_all_events(sync_profile_id=prof_id)) == 0


def test_deletion_skipped_for_invalid_status(
    sync_profile_service, sync_profile_repo, auth_service_mock
):
    """Should skip deletion for profiles in progress"""
    user_id = "user123"
    prof_id = "profile456"

    profile = _make_sync_profile(
        user_id=user_id,
        sync_profile_id=prof_id,
        status_type=SyncProfileStatusType.IN_PROGRESS,
    )
    sync_profile_repo.save_sync_profile(profile)

    sync_profile_service.delete_sync_profile(user_id, prof_id)

    # Profile still exists with original status
    assert sync_profile_repo.get_sync_profile(user_id, prof_id) is not None
    assert (
        sync_profile_repo.get_sync_profile(user_id, prof_id).status.type
        == SyncProfileStatusType.IN_PROGRESS
    )


def test_deletion_failed_authorization(
    sync_profile_service, sync_profile_repo, auth_service_mock
):
    """Should handle calendar authorization failures"""
    user_id = "user123"
    prof_id = "profile789"

    profile = _make_sync_profile(
        user_id=user_id,
        sync_profile_id=prof_id,
        status_type=SyncProfileStatusType.SUCCESS,
    )
    sync_profile_repo.save_sync_profile(profile)

    # Simulate authorization failure
    auth_service_mock.get_authenticated_google_calendar_manager.side_effect = Exception(
        "Auth failed"
    )

    sync_profile_service.delete_sync_profile(user_id, prof_id)

    updated_profile = sync_profile_repo.get_sync_profile(user_id, prof_id)
    assert updated_profile.status.type == SyncProfileStatusType.DELETION_FAILED
    assert "Authorization failed" in updated_profile.status.message


def test_deletion_failed_event_cleanup(
    sync_profile_service: SyncProfileService, sync_profile_repo, auth_service_mock
):
    """Should handle event deletion failures"""
    user_id = "user123"
    prof_id = "profile101112"

    profile = _make_sync_profile(
        user_id=user_id,
        sync_profile_id=prof_id,
        status_type=SyncProfileStatusType.SUCCESS,
    )
    sync_profile_repo.save_sync_profile(profile)

    # Mock manager that throws on delete
    manager = MockGoogleCalendarManager()
    # Create some events first
    manager.create_events(
        [Event(start=arrow.now(), end=arrow.now().shift(hours=1), title="Test Event")],
        sync_profile_id=prof_id,
    )
    # Then make delete_events throw
    manager.delete_events = Mock(side_effect=Exception("Delete failed"))
    auth_service_mock.get_authenticated_google_calendar_manager.return_value = manager

    sync_profile_service.delete_sync_profile(user_id, prof_id)

    updated_profile = sync_profile_repo.get_sync_profile(user_id, prof_id)
    # Profile should still exist, but status should be DELETION_FAILED
    assert updated_profile.status.type == SyncProfileStatusType.DELETION_FAILED
    assert "Could not delete events" in updated_profile.status.message


def test_force_sync_bypasses_status_check(
    sync_profile_service,
    sync_profile_repo,
    auth_service_mock,
    ics_service_mock,
    future_event,
    mock_event_bus,
):
    """
    Force sync should work even when profile is in IN_PROGRESS state.
    """
    user_id = "user123"
    prof_id = "profile_force"

    # Return one future event
    ics_service_mock.try_fetch_and_parse.return_value = IcsFetchAndParseResult(
        events=[future_event],
        raw_ics="mock irrelevant ics value",
    )

    # Put a profile in IN_PROGRESS state (which would normally block syncing)
    profile = _make_sync_profile(
        user_id=user_id,
        sync_profile_id=prof_id,
        status_type=SyncProfileStatusType.IN_PROGRESS,
    )
    sync_profile_repo.save_sync_profile(profile)

    manager = MockGoogleCalendarManager()
    auth_service_mock.get_authenticated_google_calendar_manager.return_value = manager

    # Act - with force=True
    sync_profile_service.synchronize(
        user_id=user_id,
        sync_profile_id=prof_id,
        sync_trigger=SyncTrigger.MANUAL,
        sync_type=SyncType.REGULAR,
        force=True,
    )

    # Event was created despite IN_PROGRESS state
    all_events = manager.get_all_events(sync_profile_id=prof_id)
    assert len(all_events) == 1
    assert all_events[0]["summary"] == "Future Event"

    # Final status is SUCCESS
    updated_profile = sync_profile_repo.get_sync_profile(user_id, prof_id)
    assert updated_profile is not None
    assert updated_profile.status.type == SyncProfileStatusType.SUCCESS
    mock_event_bus.assert_event_published_with_data(
        domain_events.SyncSucceeded,
        user_id=user_id,
        sync_profile_id=prof_id,
    )


def test_force_sync_bypasses_daily_limit(
    sync_profile_service,
    sync_profile_repo,
    auth_service_mock,
    ics_service_mock,
    sync_stats_repo,
    future_event,
    mock_event_bus,
):
    """
    Force sync should bypass the daily limit check.
    """
    from backend.settings import settings

    user_id = "userX"
    prof_id = "profile_force_limit"

    # Saturate daily limit
    for _ in range(settings.MAX_SYNCHRONIZATIONS_PER_DAY):
        sync_stats_repo.increment_sync_count(user_id)

    # Put a profile in IN_PROGRESS state
    profile = _make_sync_profile(
        user_id=user_id,
        sync_profile_id=prof_id,
        status_type=SyncProfileStatusType.IN_PROGRESS,
    )
    sync_profile_repo.save_sync_profile(profile)

    manager = MockGoogleCalendarManager()
    auth_service_mock.get_authenticated_google_calendar_manager.return_value = manager

    # Return one future event
    ics_service_mock.try_fetch_and_parse.return_value = IcsFetchAndParseResult(
        events=[future_event],
        raw_ics="mock irrelevant ics value",
    )

    # Act - with force=True
    sync_profile_service.synchronize(
        user_id=user_id,
        sync_profile_id=prof_id,
        sync_trigger=SyncTrigger.MANUAL,
        sync_type=SyncType.REGULAR,
        force=True,
    )

    # Profile should be in SUCCESS state
    updated_profile = sync_profile_repo.get_sync_profile(user_id, prof_id)
    assert updated_profile is not None
    assert updated_profile.status.type == SyncProfileStatusType.SUCCESS

    # ICS was called despite being over limit
    ics_service_mock.try_fetch_and_parse.assert_called_once()

    # Event was created despite being over limit
    all_events = manager.get_all_events(sync_profile_id=prof_id)
    assert len(all_events) == 1
    assert all_events[0]["summary"] == "Future Event"

    # Assert sync succeeded event was published (which will increment sync count)
    mock_event_bus.assert_event_published_with_data(
        domain_events.SyncSucceeded,
        user_id=user_id,
        sync_profile_id=prof_id,
    )


def test_force_sync_follows_normal_flow_on_error(
    sync_profile_service,
    sync_profile_repo,
    auth_service_mock,
    ics_service_mock,
    sync_stats_repo,
    mock_event_bus,
):
    """
    Force sync should still handle errors normally (e.g. ICS errors).
    """
    user_id = "userABC"
    prof_id = "profile_force_error"

    # Simulate ICS error
    error = IcsSourceError("Failed to fetch")
    ics_service_mock.try_fetch_and_parse.return_value = error

    # Put a profile in IN_PROGRESS state
    profile = _make_sync_profile(
        user_id=user_id,
        sync_profile_id=prof_id,
        status_type=SyncProfileStatusType.IN_PROGRESS,
    )
    sync_profile_repo.save_sync_profile(profile)

    manager = MockGoogleCalendarManager()
    auth_service_mock.get_authenticated_google_calendar_manager.return_value = manager

    # Act - with force=True
    sync_profile_service.synchronize(
        user_id=user_id,
        sync_profile_id=prof_id,
        sync_trigger=SyncTrigger.MANUAL,
        sync_type=SyncType.REGULAR,
        force=True,
    )

    # Profile should be in FAILED state with error message
    updated_profile = sync_profile_repo.get_sync_profile(user_id, prof_id)
    assert updated_profile is not None
    assert updated_profile.status.type == SyncProfileStatusType.FAILED
    assert "Failed to fetch" in updated_profile.status.message

    # No events created
    assert len(manager.get_all_events(sync_profile_id=prof_id)) == 0

    # Assert sync failed event was published (which will not increment sync count)
    mock_event_bus.assert_event_published_with_data(
        domain_events.SyncFailed,
        user_id=user_id,
        sync_profile_id=prof_id,
    )


@pytest.mark.parametrize("calendar_type", ["createNew", "useExisting"])
def test_create_sync_profile_success(
    sync_profile_service,
    sync_profile_repo,
    auth_service_mock,
    ics_service_mock,
    google_calendar_service,
    ai_ruleset_service,
    mock_event_bus,
    calendar_type,
):
    """
    Test create_sync_profile for both 'createNew' and 'useExisting' calendar flows.
    Asserts correct repo, event, and sync side effects.
    """
    user_id = "user_create"
    provider_account_id = "provider123"
    title = "My Test Profile"
    url = "https://example.com/test.ics"
    schedule_source = ScheduleSource(url=HttpUrl(url))

    fixed_uuid = "00000000-0000-4000-8000-000000000000"

    def uuid_factory():
        return fixed_uuid

    # Setup target calendar input
    if calendar_type == "createNew":
        target_calendar_input = CreateNewTargetCalendarInput(
            type="createNew",
            colorId=5,
            providerAccountId=provider_account_id,
        )
        # Mock calendar creation result
        google_calendar_service.create_new_calendar.return_value = {
            "id": "cal_new_id",
            "summary": "New Calendar",
            "description": "A new calendar",
        }
        expected_calendar_id = "cal_new_id"
        expected_calendar_title = "New Calendar"
        expected_calendar_description = "A new calendar"
    else:
        target_calendar_input = UseExistingTargetCalendarInput(
            type="useExisting",
            calendarId="existing_cal_id",
            providerAccountId=provider_account_id,
        )
        # Mock calendar lookup result
        google_calendar_service.get_calendar_by_id.return_value = {
            "id": "existing_cal_id",
            "summary": "Existing Calendar",
            "description": "Existing desc",
        }
        expected_calendar_id = "existing_cal_id"
        expected_calendar_title = "Existing Calendar"
        expected_calendar_description = "Existing desc"

    # Mock provider account email
    auth_service_mock.get_provider_account_email.return_value = "user@example.com"
    # Mock authorization test
    auth_service_mock.test_authorization.return_value = None
    # Mock ICS URL validation
    ics_service_mock.validate_ics_url_or_raise.return_value = None
    # Mock ruleset creation
    ai_ruleset_service.create_ruleset_for_sync_profile.return_value = None
    # Mock synchronize (don't actually run sync logic)
    sync_profile_service.synchronize = Mock()

    request = CreateSyncProfileInput(
        title=title,
        scheduleSource=schedule_source,
        targetCalendar=target_calendar_input,
    )

    # Act
    result = sync_profile_service.create_sync_profile(
        user_id=user_id,
        request=request,
        uuid_factory=uuid_factory,
    )

    # Assert profile in repo
    saved_profile = sync_profile_repo.get_sync_profile(user_id, fixed_uuid)
    assert saved_profile is not None
    assert saved_profile.title == title
    assert str(saved_profile.scheduleSource.url) == url
    assert saved_profile.targetCalendar.id == expected_calendar_id
    assert saved_profile.targetCalendar.title == expected_calendar_title
    assert saved_profile.targetCalendar.description == expected_calendar_description
    assert saved_profile.targetCalendar.providerAccountId == provider_account_id
    assert saved_profile.targetCalendar.providerAccountEmail == "user@example.com"
    assert saved_profile.status.type == SyncProfileStatusType.NOT_STARTED
    # ruleset and ruleset_error should be None
    assert saved_profile.ruleset is None
    assert saved_profile.ruleset_error is None

    # Assert event published
    mock_event_bus.assert_event_published_with_data(
        domain_events.SyncProfileCreated,
        user_id=user_id,
        sync_profile_id=fixed_uuid,
    )

    # Assert ruleset creation called
    ai_ruleset_service.create_ruleset_for_sync_profile.assert_called_once()
    # Assert synchronize called for initial sync
    sync_profile_service.synchronize.assert_called_once_with(
        user_id=user_id,
        sync_profile_id=fixed_uuid,
        sync_trigger=SyncTrigger.ON_CREATE,
    )


def test_create_sync_profile_existing_calendar_not_found(
    sync_profile_service,
    auth_service_mock,
    ics_service_mock,
    google_calendar_service,
    mock_event_bus,
):
    """
    Test create_sync_profile raises TargetCalendarNotFoundError if existing calendar is not found.
    """
    user_id = "user_create"
    provider_account_id = "provider123"
    title = "My Test Profile"
    url = "https://example.com/test.ics"
    schedule_source = ScheduleSource(url=HttpUrl(url))
    target_calendar_input = UseExistingTargetCalendarInput(
        type="useExisting",
        calendarId="missing_cal_id",
        providerAccountId=provider_account_id,
    )
    # Mock calendar lookup result: not found
    google_calendar_service.get_calendar_by_id.return_value = None
    # Mock authorization test
    auth_service_mock.test_authorization.return_value = None
    # Mock ICS URL validation
    ics_service_mock.validate_ics_url_or_raise.return_value = None

    request = CreateSyncProfileInput(
        title=title,
        scheduleSource=schedule_source,
        targetCalendar=target_calendar_input,
    )

    with pytest.raises(TargetCalendarNotFoundError):
        sync_profile_service.create_sync_profile(user_id, request)

    # Assert event was published
    mock_event_bus.assert_event_published_with_data(
        domain_events.SyncProfileCreationFailed,
        user_id=user_id,
    )


def test_create_sync_profile_unauthorized(
    sync_profile_service,
    auth_service_mock,
    ics_service_mock,
    google_calendar_service,
):
    """
    Test create_sync_profile raises if test_authorization fails.
    """
    user_id = "user_create"
    provider_account_id = "provider123"
    title = "My Test Profile"
    url = "https://example.com/test.ics"
    schedule_source = ScheduleSource(url=HttpUrl(url))
    target_calendar_input = CreateNewTargetCalendarInput(
        type="createNew",
        colorId=5,
        providerAccountId=provider_account_id,
    )
    # Mock authorization test to raise
    auth_service_mock.test_authorization.side_effect = Exception("unauthorized")

    request = CreateSyncProfileInput(
        title=title,
        scheduleSource=schedule_source,
        targetCalendar=target_calendar_input,
    )

    with pytest.raises(Exception) as exc_info:
        sync_profile_service.create_sync_profile(user_id, request)
    assert "unauthorized" in str(exc_info.value)


def test_create_sync_profile_invalid_ics_url(
    sync_profile_service,
    auth_service_mock,
    ics_service_mock,
    google_calendar_service,
):
    """
    Test create_sync_profile raises if ICS URL validation fails.
    """
    user_id = "user_create"
    provider_account_id = "provider123"
    title = "My Test Profile"
    url = "https://example.com/test.ics"
    schedule_source = ScheduleSource(url=HttpUrl(url))
    target_calendar_input = CreateNewTargetCalendarInput(
        type="createNew",
        colorId=5,
        providerAccountId=provider_account_id,
    )
    # Mock authorization test
    auth_service_mock.test_authorization.return_value = None
    # Mock ICS URL validation to raise
    ics_service_mock.validate_ics_url_or_raise.side_effect = Exception(
        "invalid ics url"
    )

    request = CreateSyncProfileInput(
        title=title,
        scheduleSource=schedule_source,
        targetCalendar=target_calendar_input,
    )

    with pytest.raises(Exception) as exc_info:
        sync_profile_service.create_sync_profile(user_id, request)
    assert "invalid ics url" in str(exc_info.value)
