import 'dart:async';

import '../models/id.dart';

import '../models/schedule_source.dart';

import '../models/sync_profile.dart';

abstract class SyncProfileRepository {
  Future<SyncProfile?> getSyncProfile(ID id);
  Stream<List<SyncProfile>> getSyncProfiles();

  Future<void> createSyncProfile(SyncProfile syncProfile);
  Future<void> updateSyncProfile(SyncProfile syncProfile);
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
      final scheduleSourceId = ID();
      final scheduleSource = ScheduleSource(
          id: scheduleSourceId,
          url:
              'https://insa-moncuq.fr/ade/emploi-du-temps/${scheduleSourceId.value}');

      final id = ID();
      final syncProfile = SyncProfile(id: id, scheduleSource: scheduleSource);
      _syncProfiles[id] = syncProfile;
    }
  }
}
