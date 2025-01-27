from datetime import date
from freezegun import freeze_time

from functions.repositories.sync_stats_repository import MockSyncStatsRepository


def test_get_daily_sync_count_returns_zero_for_new_user() -> None:
    """Should return 0 for a user that hasn't synced yet."""
    repo = MockSyncStatsRepository()
    assert repo.get_daily_sync_count("non_existent_user") == 0


def test_increment_sync_count_increases_count() -> None:
    """Should increment the sync count for a user."""
    repo = MockSyncStatsRepository()
    user_id = "test_user"

    repo.increment_sync_count(user_id)
    assert repo.get_daily_sync_count(user_id) == 1

    repo.increment_sync_count(user_id)
    assert repo.get_daily_sync_count(user_id) == 2


def test_sync_counts_are_separate_for_different_users() -> None:
    """Should maintain separate counts for different users."""
    repo = MockSyncStatsRepository()
    user1 = "user1"
    user2 = "user2"

    repo.increment_sync_count(user1)
    repo.increment_sync_count(user1)
    repo.increment_sync_count(user2)

    assert repo.get_daily_sync_count(user1) == 2
    assert repo.get_daily_sync_count(user2) == 1


def test_sync_counts_are_separate_for_different_dates() -> None:
    """Should maintain separate counts for different dates."""
    repo = MockSyncStatsRepository()
    user_id = "test_user"
    date1 = date(2024, 1, 1)
    date2 = date(2024, 1, 2)

    repo.increment_sync_count(user_id, date1)
    repo.increment_sync_count(user_id, date1)
    repo.increment_sync_count(user_id, date2)

    assert repo.get_daily_sync_count(user_id, date1) == 2
    assert repo.get_daily_sync_count(user_id, date2) == 1


@freeze_time("2024-01-15")
def test_default_date_uses_today() -> None:
    """Should use today's date when no date is specified."""
    repo = MockSyncStatsRepository()
    user_id = "test_user"
    today = date(2024, 1, 15)

    repo.increment_sync_count(user_id)
    assert repo.get_daily_sync_count(user_id) == 1
    assert repo.get_daily_sync_count(user_id, today) == 1

    # Verify different date returns 0
    other_date = date(2024, 1, 14)
    assert repo.get_daily_sync_count(user_id, other_date) == 0
