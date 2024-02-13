import 'package:syncademic_app/models/schedule_source.dart';

import '../models/sync_profile.dart';
import '../models/types.dart';

abstract class SyncProfileRepository {
  Future<SyncProfile?> getSyncProfile(ID id);
  Stream<List<SyncProfile>> getSyncProfiles();

  Future<void> createSyncProfile(SyncProfile syncProfile);
  Future<void> updateSyncProfile(SyncProfile syncProfile);
}

class MockSyncProfileRepository implements SyncProfileRepository {
  final Map<ID, SyncProfile> _syncProfiles = {};

  @override
  Future<SyncProfile?> getSyncProfile(ID id) async {
    return _syncProfiles[id];
  }

  @override
  Stream<List<SyncProfile>> getSyncProfiles() async* {
    yield _syncProfiles.values.toList();
  }

  @override
  Future<void> createSyncProfile(SyncProfile syncProfile) async {
    if (_syncProfiles.containsKey(syncProfile.id)) {
      throw Exception('SyncProfile already exists');
    }

    _syncProfiles[syncProfile.id] = syncProfile;
  }

  @override
  Future<void> updateSyncProfile(SyncProfile syncProfile) async {
    _syncProfiles[syncProfile.id] = syncProfile;
  }

  void createRandomData(int n) {
    for (var i = 0; i < n; i++) {
      final scheduleSource = ScheduleSource(
          id: 'scheduleSource$i',
          url: 'https://insa-moncuq.fr/ade/emploi-du-temps/$i');

      final syncProfile =
          SyncProfile(id: 'syncProfile$i', scheduleSource: scheduleSource);
      _syncProfiles['$i'] = syncProfile;
    }
  }
}
