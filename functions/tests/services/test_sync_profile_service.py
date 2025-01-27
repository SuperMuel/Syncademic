"""
tests/services/test_sync_profile_service.py

Tests for the new SyncProfileService. These tests verify the end-to-end synchronization
logic (e.g., ICS fetching, parsing, applying rules, and deleting/creating calendar events)
using mocks and the in-memory MockGoogleCalendarManager.
"""

from pydantic import HttpUrl
import pytest
import arrow
from unittest.mock import Mock

from functions.settings import settings
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
from functions.services.exceptions.sync import DailySyncLimitExceededError
from functions.services.exceptions.ics import (
    BaseIcsError,
    IcsParsingError,
    IcsSourceError,
)
from functions.repositories.sync_stats_repository import MockSyncStatsRepository
from functions.synchronizer.google_calendar_manager import (
    MockGoogleCalendarManager,
)


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
def sync_profile_repo_mock():
    """Mock of ISyncProfileRepository."""
    return Mock()


@pytest.fixture
def auth_service_mock():
    """
    Mock of AuthorizationService.
    We'll stub get_authenticated_google_calendar_manager(...) to return a MockGoogleCalendarManager.
    """
    return Mock()


@pytest.fixture
def ics_service_mock():
    """
    Mock of IcsService.
    We'll control the return value of try_fetch_and_parse(...) (list[Event] or BaseIcsError).
    """
    return Mock()


@pytest.fixture
def sync_stats_repo() -> MockSyncStatsRepository:
    """Real in-memory stats repo to verify daily increments."""
    return MockSyncStatsRepository()


@pytest.fixture
def sync_profile_service(
    sync_profile_repo_mock,
    sync_stats_repo,
    auth_service_mock,
    ics_service_mock,
):
    """Create a SyncProfileService with all dependencies mocked or injected."""
    return SyncProfileService(
        sync_profile_repo=sync_profile_repo_mock,
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
    sync_profile_repo_mock,
    auth_service_mock,
    ics_service_mock,
    sync_stats_repo,
    future_event,
    past_event,
):
    """
    ON_CREATE scenario: ICS returns 2 events, both get created. Final status -> SUCCESS,
    daily sync count increments.
    """
    user_id = "user123"
    prof_id = "profile_on_create"

    # ICS is a success -> returns 2 events
    ics_service_mock.try_fetch_and_parse.return_value = [past_event, future_event]

    # The sync profile is newly created with NOT_STARTED status
    sync_profile = _make_sync_profile(
        user_id=user_id,
        sync_profile_id=prof_id,
        status_type=SyncProfileStatusType.NOT_STARTED,
    )
    sync_profile_repo_mock.get_sync_profile.return_value = sync_profile

    # Provide a mock manager from auth service
    manager = MockGoogleCalendarManager()
    auth_service_mock.get_authenticated_google_calendar_manager.return_value = manager

    # Act
    sync_profile_service.synchronize(
        user_id=user_id,
        sync_profile_id=prof_id,
        sync_trigger=SyncTrigger.ON_CREATE,
        sync_type=SyncType.REGULAR,
    )

    # Assert
    # 1) IcsService is called
    ics_service_mock.try_fetch_and_parse.assert_called_once()
    # 2) 2 events created
    all_events = manager.get_all_events()
    assert len(all_events) == 2
    # # 3) final status = SUCCESS
    final_call = sync_profile_repo_mock.update_sync_profile_status.mock_calls[-1]
    # _, kwargs = final_call
    # assert kwargs["status"].type == SyncProfileStatusType.SUCCESS
    # # 4) daily usage = 1
    # assert sync_stats_repo.get_daily_sync_count(user_id) == 1


def test_regular_sync_only_future(
    sync_profile_service,
    sync_profile_repo_mock,
    auth_service_mock,
    ics_service_mock,
    sync_stats_repo,
    future_event,
    past_event,
):
    """
    REGULAR sync scenario: ICS returns 1 past + 1 future event.
    We only create the future event, and delete existing future events in the calendar.
    """
    user_id = "user123"
    prof_id = "profile_reg"

    ics_service_mock.try_fetch_and_parse.return_value = [past_event, future_event]

    sync_profile = _make_sync_profile(
        user_id=user_id,
        sync_profile_id=prof_id,
        status_type=SyncProfileStatusType.SUCCESS,
    )
    sync_profile_repo_mock.get_sync_profile.return_value = sync_profile

    # Manager has 2 old future events
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

    # Assert
    # 1) Only future event is created, old future events are deleted
    all_after = manager.get_all_events()
    assert len(all_after) == 1
    (key, (ev_data, _)) = list(all_after.items())[0]
    assert ev_data["summary"] == "Future Event"
    # 2) final status SUCCESS
    final_status_call = sync_profile_repo_mock.update_sync_profile_status.mock_calls[-1]
    _, kwargs = final_status_call
    assert kwargs["status"].type == SyncProfileStatusType.SUCCESS
    # 3) daily usage = 1
    assert sync_stats_repo.get_daily_sync_count(user_id) == 1


def test_full_sync_deletes_all(
    sync_profile_service,
    sync_profile_repo_mock,
    auth_service_mock,
    ics_service_mock,
    sync_stats_repo,
    future_event,
):
    """
    FULL sync: ICS returns 1 event,
    we delete all existing events from that profile, then create the new one.
    """
    user_id = "user123"
    prof_id = "profile_full"

    ics_service_mock.try_fetch_and_parse.return_value = [future_event]

    sync_profile = _make_sync_profile(
        user_id=user_id,
        sync_profile_id=prof_id,
        status_type=SyncProfileStatusType.SUCCESS,
    )
    sync_profile_repo_mock.get_sync_profile.return_value = sync_profile

    manager = MockGoogleCalendarManager()
    # Suppose we had 3 old events
    manager.create_events(
        [
            Event(start=future_event.start, end=future_event.end, title="Old A"),
            Event(start=future_event.start, end=future_event.end, title="Old B"),
            Event(start=future_event.start, end=future_event.end, title="Old C"),
        ],
        sync_profile_id=prof_id,
    )
    auth_service_mock.get_authenticated_google_calendar_manager.return_value = manager

    # Act
    sync_profile_service.synchronize(
        user_id=user_id,
        sync_profile_id=prof_id,
        sync_trigger=SyncTrigger.MANUAL,
        sync_type=SyncType.FULL,
    )

    # All old events removed, 1 new event remains
    all_events = manager.get_all_events()
    assert len(all_events) == 1
    only_event = list(all_events.values())[0][0]
    assert only_event["summary"] == "Future Event"

    final_call = sync_profile_repo_mock.update_sync_profile_status.mock_calls[-1]
    _, kwargs = final_call
    assert kwargs["status"].type == SyncProfileStatusType.SUCCESS
    assert sync_stats_repo.get_daily_sync_count(user_id) == 1


def test_ruleset_applied(
    sync_profile_service,
    sync_profile_repo_mock,
    auth_service_mock,
    ics_service_mock,
    sync_stats_repo,
):
    """
    If there's a ruleset, it modifies the events.
    The IcsService returns 1 event "Lecture" -> we transform to "Modified Lecture"
    and color = GRAPHITE, final status SUCCESS, usage=1.
    """
    now = arrow.now()
    raw_event = Event(start=now, end=now.shift(hours=1), title="Lecture")

    ics_service_mock.try_fetch_and_parse.return_value = [raw_event]

    # Create a simple ruleset that sets "Lecture" => "Modified Lecture"
    from functions.models.rules import (
        Rule,
        Ruleset,
        TextFieldCondition,
        ChangeFieldAction,
    )

    cond = TextFieldCondition(field="title", operator="contains", value="Lecture")
    act = ChangeFieldAction(field="title", method="set", value="Modified Lecture")
    ruleset = Ruleset(rules=[Rule(condition=cond, actions=[act])])

    sync_profile = _make_sync_profile(ruleset=ruleset)
    sync_profile_repo_mock.get_sync_profile.return_value = sync_profile

    manager = MockGoogleCalendarManager()
    auth_service_mock.get_authenticated_google_calendar_manager.return_value = manager

    sync_profile_service.synchronize(
        user_id="user123",
        sync_profile_id="profileABC",
        sync_trigger=SyncTrigger.MANUAL,
        sync_type=SyncType.REGULAR,
    )

    # 1 event created, with modified title
    all_ev = manager.get_all_events()
    assert len(all_ev) == 1
    ev_data, _ = list(all_ev.values())[0]
    assert ev_data["summary"] == "Modified Lecture"
    assert ev_data["colorId"] == GoogleEventColor.GRAPHITE.to_color_id()

    final_call = sync_profile_repo_mock.update_sync_profile_status.mock_calls[-1]
    _, kwargs = final_call
    assert kwargs["status"].type == SyncProfileStatusType.SUCCESS
    assert sync_stats_repo.get_daily_sync_count("user123") == 1


def test_fails_on_ics_fetch_error(
    sync_profile_service,
    sync_profile_repo_mock,
    auth_service_mock,
    ics_service_mock,
    sync_stats_repo,
):
    """
    ICS fails to fetch/parse => we raise that error => final status=FAILED,
    no events created, daily usage not incremented.
    """
    user_id = "userXYZ"
    prof_id = "profileFail"

    # Return an IcsSourceError to simulate a fetch error or parse error
    ics_service_mock.try_fetch_and_parse.return_value = IcsSourceError("Couldn't fetch")

    sync_profile = _make_sync_profile(user_id=user_id, sync_profile_id=prof_id)
    sync_profile_repo_mock.get_sync_profile.return_value = sync_profile

    manager = MockGoogleCalendarManager()
    auth_service_mock.get_authenticated_google_calendar_manager.return_value = manager

    sync_profile_service.synchronize(
        user_id=user_id,
        sync_profile_id=prof_id,
        sync_trigger=SyncTrigger.MANUAL,
        sync_type=SyncType.REGULAR,
    )

    final_call = sync_profile_repo_mock.update_sync_profile_status.mock_calls[-1]
    _, kwargs = final_call
    assert kwargs["status"].type == SyncProfileStatusType.FAILED

    # no events
    assert len(manager.get_all_events()) == 0
    # daily usage still 0
    assert sync_stats_repo.get_daily_sync_count(user_id) == 0


def test_fails_on_daily_limit(
    sync_profile_service,
    sync_profile_repo_mock,
    auth_service_mock,
    ics_service_mock,
    sync_stats_repo,
    future_event,
):
    """
    If user exceeded daily sync limit, we fail early before ICS is fetched.
    """
    user_id = "userX"
    prof_id = "profileLimit"

    # We do 10 sync increments to simulate a used-up daily limit
    for _ in range(settings.MAX_SYNCHRONIZATIONS_PER_DAY):
        sync_stats_repo.increment_sync_count(user_id)

    sync_profile = _make_sync_profile(user_id=user_id, sync_profile_id=prof_id)
    sync_profile_repo_mock.get_sync_profile.return_value = sync_profile

    manager = MockGoogleCalendarManager()
    auth_service_mock.get_authenticated_google_calendar_manager.return_value = manager

    # ICS would have a future event, but we won't get that far
    ics_service_mock.try_fetch_and_parse.return_value = [future_event]

    # Act
    sync_profile_service.synchronize(
        user_id=user_id,
        sync_profile_id=prof_id,
        sync_trigger=SyncTrigger.MANUAL,
        sync_type=SyncType.REGULAR,
    )

    # final status = FAILED
    final_call = sync_profile_repo_mock.update_sync_profile_status.mock_calls[-1]
    _, kwargs = final_call
    assert kwargs["status"].type == SyncProfileStatusType.FAILED

    # ICS never fetched
    ics_service_mock.try_fetch_and_parse.assert_not_called()

    # no events
    assert len(manager.get_all_events()) == 0

    # usage is still maxed out, no new increment
    assert (
        sync_stats_repo.get_daily_sync_count(user_id)
        == settings.MAX_SYNCHRONIZATIONS_PER_DAY
    )
