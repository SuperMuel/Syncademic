import 'package:flutter_test/flutter_test.dart';
import 'package:syncademic_app/models/id.dart';
import 'package:syncademic_app/models/schedule_source.dart';
import 'package:syncademic_app/models/sync_profile.dart';
import 'package:syncademic_app/models/sync_profile_status.dart';
import 'package:syncademic_app/models/target_calendar.dart';
import 'package:syncademic_app/screens/sync_profile/cubit/sync_profile_cubit.dart';

const scheduleSource1 = ScheduleSource(url: "https://example.com");
final targetCalendar1 = TargetCalendar(
  id: ID(),
  title: "Calendar 1",
  description: "Description 1",
  providerAccountId: "6371892",
  createdBySyncademic: true,
);

SyncProfile getSyncProfile({
  required SyncProfileStatus status,
  ID? id,
  String? title,
  ScheduleSource? scheduleSource,
  TargetCalendar? targetCalendar,
}) =>
    SyncProfile(
      id: id ?? ID(),
      title: "Title",
      status: status,
      scheduleSource: scheduleSource ?? scheduleSource1,
      targetCalendar: targetCalendar ?? targetCalendar1,
    );

void main() {
  group('canRequestSync', () {
    test('sync already in progress', () {
      final syncProfile = getSyncProfile(
        status: const SyncProfileStatus.inProgress(),
      );
      final state = SyncProfileState.loaded(syncProfile);

      expect(state.canRequestSync, isFalse);
    });

    test('last sync request was less than kMinSyncInterval ago', () {
      final syncProfile = getSyncProfile(
        status: const SyncProfileStatus.success(),
      );
      final state =
          SyncProfileState.loaded(syncProfile, lastSyncRequest: DateTime.now());

      expect(state.canRequestSync, isFalse);
    });

    test('last sync request was more than kMinSyncInterval ago', () {
      final syncProfile = getSyncProfile(
        status: const SyncProfileStatus.success(),
      );
      final state = SyncProfileState.loaded(
        syncProfile,
        lastSyncRequest:
            DateTime.now().subtract(SyncProfileState.kMinSyncInterval * 2),
      );

      expect(state.canRequestSync, isTrue);
    });
  });
}
