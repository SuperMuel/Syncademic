from pydantic import HttpUrl
import pytest
import arrow
from unittest.mock import Mock

from functions.models.sync_profile import (
    SyncProfile,
    SyncProfileStatus,
    SyncProfileStatusType,
    SyncTrigger,
    SyncType,
    ScheduleSource,
    TargetCalendar,
)
from functions.shared.event import Event
from functions.shared.google_calendar_colors import GoogleEventColor
from functions.services.sync_profile_service import SyncProfileService
from functions.services.exceptions.ics import (
    IcsSourceError,
)
from functions.repositories.sync_stats_repository import MockSyncStatsRepository
from functions.repositories.sync_profile_repository import MockSyncProfileRepository
from functions.synchronizer.google_calendar_manager import MockGoogleCalendarManager


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
    We'll control the return value of try_fetch_and_parse(...) (list[Event] or a BaseIcsError).
    """
    return Mock()


@pytest.fixture
def sync_stats_repo() -> MockSyncStatsRepository:
    """Real in-memory stats repo to verify daily increments."""
    return MockSyncStatsRepository()


@pytest.fixture
def sync_profile_service(
    sync_profile_repo,
    sync_stats_repo,
    auth_service_mock,
    ics_service_mock,
):
    """Create a SyncProfileService with the real MockSyncProfileRepository."""
    return SyncProfileService(
        sync_profile_repo=sync_profile_repo,
        sync_stats_repo=sync_stats_repo,
        authorization_service=auth_service_mock,
        ics_service=ics_service_mock,
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


def test_on_create_success(
    sync_profile_service,
    sync_profile_repo,
    auth_service_mock,
    ics_service_mock,
    sync_stats_repo,
    future_event,
    past_event,
):
    """
    ON_CREATE scenario: ICS returns 2 events, both get created.
    We store the profile in memory with status=NOT_STARTED,
    then check final status in the repo after sync.
    """
    user_id = "user123"
    prof_id = "profile_on_create"

    # ICS returns 2 events
    ics_service_mock.try_fetch_and_parse.return_value = [past_event, future_event]

    # Put a NOT_STARTED profile into the repository
    profile = _make_sync_profile(
        user_id=user_id,
        sync_profile_id=prof_id,
        status_type=SyncProfileStatusType.NOT_STARTED,
    )
    sync_profile_repo.store_sync_profile(profile)

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

    # daily usage = 1
    assert sync_stats_repo.get_daily_sync_count(user_id) == 1


def test_regular_sync_only_future(
    sync_profile_service,
    sync_profile_repo,
    auth_service_mock,
    ics_service_mock,
    sync_stats_repo,
    future_event,
    past_event,
):
    """
    REGULAR sync scenario: ICS returns 1 past + 1 future event.
    Sync should only create the future event, and delete old future events.
    """
    user_id = "user123"
    prof_id = "profile_reg"

    ics_service_mock.try_fetch_and_parse.return_value = [past_event, future_event]

    # Put a profile in SUCCESS state
    profile = _make_sync_profile(
        user_id=user_id,
        sync_profile_id=prof_id,
        status_type=SyncProfileStatusType.SUCCESS,
    )
    sync_profile_repo.store_sync_profile(profile)

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

    # daily usage = 1
    assert sync_stats_repo.get_daily_sync_count(user_id) == 1


def test_full_sync_deletes_all(
    sync_profile_service,
    sync_profile_repo,
    auth_service_mock,
    ics_service_mock,
    sync_stats_repo,
    past_event,
    future_event,
):
    """
    FULL sync: ICS returns 1 event, we remove all old events, create the new one.
    """
    user_id = "user123"
    prof_id = "profile_full"

    ics_service_mock.try_fetch_and_parse.return_value = [future_event]

    profile = _make_sync_profile(
        user_id=user_id,
        sync_profile_id=prof_id,
        status_type=SyncProfileStatusType.SUCCESS,
    )
    sync_profile_repo.store_sync_profile(profile)

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
    assert sync_stats_repo.get_daily_sync_count(user_id) == 1


def test_ruleset_applied(
    sync_profile_service,
    sync_profile_repo,
    auth_service_mock,
    ics_service_mock,
    sync_stats_repo,
):
    """
    ICS returns 1 event "Lecture", we have a ruleset that changes it to "Modified Lecture".
    Then we confirm the final status in the repository.
    """
    now = arrow.now()
    raw_event = Event(start=now, end=now.shift(hours=1), title="Lecture")
    ics_service_mock.try_fetch_and_parse.return_value = [raw_event]

    from functions.models.rules import (
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
    sync_profile_repo.store_sync_profile(profile)

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
    assert sync_stats_repo.get_daily_sync_count(user_id) == 1


def test_fails_on_ics_fetch_error(
    sync_profile_service,
    sync_profile_repo,
    auth_service_mock,
    ics_service_mock,
    sync_stats_repo,
):
    """
    ICS returns an IcsSourceError => final status=FAILED in repository, no events, usage=0.
    """
    user_id = "userXYZ"
    prof_id = "profileFail"

    ics_service_mock.try_fetch_and_parse.return_value = IcsSourceError("Couldn't fetch")

    profile = _make_sync_profile(user_id=user_id, sync_profile_id=prof_id)
    sync_profile_repo.store_sync_profile(profile)

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
    assert sync_stats_repo.get_daily_sync_count(user_id) == 0


def test_fails_on_ics_parse_error(
    sync_profile_service,
    sync_profile_repo,
    auth_service_mock,
    ics_service_mock,
    sync_stats_repo,
):
    """
    ICS returns an IcsParseError => final status=FAILED in repository, no events, usage=0.
    """
    user_id = "userABC"
    prof_id = "profileParseError"

    # Simulate ICS parse error
    ics_service_mock.try_fetch_and_parse.side_effect = IcsSourceError(
        "Failed to parse ICS"
    )

    # Store initial profile
    profile = _make_sync_profile(user_id=user_id, sync_profile_id=prof_id)
    sync_profile_repo.store_sync_profile(profile)

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

    # Assert sync count was not incremented
    assert sync_stats_repo.get_daily_sync_count(user_id) == 0


def test_fails_on_daily_limit(
    sync_profile_service,
    sync_profile_repo,
    auth_service_mock,
    ics_service_mock,
    sync_stats_repo,
    future_event,
):
    """
    If user exceeded daily limit, we fail early (status=FAILED in the repo),
    ICS not fetched, no events, usage doesn't increment.
    """
    # We'll saturate today's usage
    from functions.settings import settings

    user_id = "userX"
    prof_id = "profileLimit"

    for _ in range(settings.MAX_SYNCHRONIZATIONS_PER_DAY):
        sync_stats_repo.increment_sync_count(user_id)

    profile = _make_sync_profile(user_id=user_id, sync_profile_id=prof_id)
    sync_profile_repo.store_sync_profile(profile)

    manager = MockGoogleCalendarManager()
    auth_service_mock.get_authenticated_google_calendar_manager.return_value = manager

    # If ICS were fetched, we'd return future_event, but we won't get that far:
    ics_service_mock.try_fetch_and_parse.return_value = [future_event]

    sync_profile_service.synchronize(
        user_id=user_id,
        sync_profile_id=prof_id,
        sync_trigger=SyncTrigger.MANUAL,
        sync_type=SyncType.REGULAR,
    )

    updated_profile = sync_profile_repo.get_sync_profile(user_id, prof_id)
    assert updated_profile is not None
    assert updated_profile.status.type == SyncProfileStatusType.FAILED

    # ICS never called
    ics_service_mock.try_fetch_and_parse.assert_not_called()

    # No new events
    assert len(manager.get_all_events(sync_profile_id=prof_id)) == 0

    # usage remains maxed
    assert (
        sync_stats_repo.get_daily_sync_count(user_id)
        == settings.MAX_SYNCHRONIZATIONS_PER_DAY
    )


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
    sync_profile_repo.store_sync_profile(profile)

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
    sync_profile_repo.store_sync_profile(profile)

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
    sync_profile_repo.store_sync_profile(profile)

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
    sync_profile_repo.store_sync_profile(profile)

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
    sync_stats_repo,
    future_event,
):
    """
    Force sync should work even when profile is in IN_PROGRESS state.
    """
    user_id = "user123"
    prof_id = "profile_force"

    # Return one future event
    ics_service_mock.try_fetch_and_parse.return_value = [future_event]

    # Put a profile in IN_PROGRESS state (which would normally block syncing)
    profile = _make_sync_profile(
        user_id=user_id,
        sync_profile_id=prof_id,
        status_type=SyncProfileStatusType.IN_PROGRESS,
    )
    sync_profile_repo.store_sync_profile(profile)

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
    assert sync_stats_repo.get_daily_sync_count(user_id) == 1


def test_force_sync_bypasses_daily_limit(
    sync_profile_service,
    sync_profile_repo,
    auth_service_mock,
    ics_service_mock,
    sync_stats_repo,
    future_event,
):
    """
    Force sync should bypass the daily limit check.
    """
    from functions.settings import settings

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
    sync_profile_repo.store_sync_profile(profile)

    manager = MockGoogleCalendarManager()
    auth_service_mock.get_authenticated_google_calendar_manager.return_value = manager

    # Return one future event
    ics_service_mock.try_fetch_and_parse.return_value = [future_event]

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

    # Usage was incremented beyond the max
    assert (
        sync_stats_repo.get_daily_sync_count(user_id)
        == settings.MAX_SYNCHRONIZATIONS_PER_DAY + 1
    )


def test_force_sync_follows_normal_flow_on_error(
    sync_profile_service,
    sync_profile_repo,
    auth_service_mock,
    ics_service_mock,
    sync_stats_repo,
):
    """
    Force sync should still handle errors normally (e.g. ICS errors).
    """
    user_id = "userABC"
    prof_id = "profile_force_error"

    # Simulate ICS error
    ics_service_mock.try_fetch_and_parse.side_effect = IcsSourceError("Failed to fetch")

    # Put a profile in IN_PROGRESS state
    profile = _make_sync_profile(
        user_id=user_id,
        sync_profile_id=prof_id,
        status_type=SyncProfileStatusType.IN_PROGRESS,
    )
    sync_profile_repo.store_sync_profile(profile)

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

    # Usage not incremented due to error
    assert sync_stats_repo.get_daily_sync_count(user_id) == 0
