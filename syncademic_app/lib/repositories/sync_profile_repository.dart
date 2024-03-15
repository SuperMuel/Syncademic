import 'dart:async';

import '../models/id.dart';
import '../models/schedule_source.dart';
import '../models/sync_profile.dart';
import '../models/target_calendar.dart';

abstract class SyncProfileRepository {
  Future<SyncProfile?> getSyncProfile(ID id);
  Stream<List<SyncProfile>> getSyncProfiles();

  Future<void> createSyncProfile(SyncProfile syncProfile);
  Future<void> updateSyncProfile(SyncProfile syncProfile);
  Stream<SyncProfile?> watchSyncProfile(ID id);

  Future<void> deleteSyncProfile(ID id);
}

class MockSyncProfileRepository implements SyncProfileRepository {
  final Map<ID, SyncProfile> _syncProfiles = {};

  // Stream controller for the getSyncProfiles method
  final _syncProfilesController =
      StreamController<List<SyncProfile>>.broadcast();

  @override
  Future<SyncProfile?> getSyncProfile(ID id) async {
    return _syncProfiles[id];
  }

  @override
  Stream<List<SyncProfile>> getSyncProfiles() async* {
    yield _syncProfiles.values.toList();
    yield* _syncProfilesController.stream;
  }

  @override
  Future<void> createSyncProfile(SyncProfile syncProfile) async {
    if (_syncProfiles.containsKey(syncProfile.id)) {
      throw Exception('SyncProfile already exists');
    }

    _syncProfiles[syncProfile.id] = syncProfile;

    _syncProfilesController.add(_syncProfiles.values.toList());
  }

  @override
  Future<void> updateSyncProfile(SyncProfile syncProfile) async {
    _syncProfiles[syncProfile.id] = syncProfile;

    _syncProfilesController.add(_syncProfiles.values.toList());
  }

  void createRandomData(int n) {
    for (var i = 0; i < n; i++) {
      ID id = ID();

      final scheduleSource = ScheduleSource(
          url: 'https://insa-moncuq.fr/ade/emploi-du-temps/${id.value}');

      // Create a target calendar
      id = ID();

      final targetCalendar = TargetCalendar(
        id: ID.fromTrustedSource('target-google-calendar-${id.value}'),
        title: 'Calendar ${id.value}',
      );

      id = ID();
      final syncProfile = SyncProfile(
        id: id,
        title: 'Sync Profile n°${id.value}',
        scheduleSource: scheduleSource,
        targetCalendar: targetCalendar,
        enabled: i % 2 == 0,
      );
      _syncProfiles[id] = syncProfile;
    }
  }

  @override
  Stream<SyncProfile?> watchSyncProfile(ID id) {
    return Stream.value(_syncProfiles[id]);
  }

  @override
  Future<void> deleteSyncProfile(ID id) async {
    _syncProfiles.remove(id);
    _syncProfilesController.add(_syncProfiles.values.toList());
  }
}
