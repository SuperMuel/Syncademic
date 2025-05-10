import 'dart:async';
import 'dart:math';

import 'package:syncademic_app/models/create_sync_profile_payload.dart';

import '../models/id.dart';
import '../models/schedule_source.dart';
import '../models/sync_profile.dart';
import '../models/sync_profile_status.dart';
import '../models/target_calendar.dart';

abstract class SyncProfileRepository {
  Future<SyncProfile?> getSyncProfile(ID id);
  Stream<List<SyncProfile>> getSyncProfiles();

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

  SyncProfile createRandomProfile() {
    ID id = ID();

    final scheduleSource = ScheduleSource(
        url: 'https://insa-moncuq.fr/ade/emploi-du-temps/${id.value}');

    // Create a target calendar
    id = ID();

    final targetCalendar = TargetCalendar(
      id: ID.fromString('target-google-calendar-${id.value}'),
      title: 'Calendar ${id.value}',
      description: 'Description of calendar ${id.value}',
      providerAccountId: 'providerAccountId',
      providerAccountEmail: 'test@syncademic.io',
    );

    int seconds = Random().nextInt(60);
    int minutes = Random().nextInt(2) * Random().nextInt(60);
    int hours = minutes == 0 ? 0 : Random().nextInt(2) * Random().nextInt(24);
    int days = hours == 0 ? 0 : Random().nextInt(2) * Random().nextInt(30);

    int totalSeconds = seconds + minutes * 60 + hours * 3600 + days * 86400;

    id = ID();
    return SyncProfile(
      id: id,
      title: 'Sync Profile n°${id.value}',
      scheduleSource: scheduleSource,
      targetCalendar: targetCalendar,
      lastSuccessfulSync:
          DateTime.now().subtract(Duration(seconds: totalSeconds)),
      status: SyncProfileStatus.success(
        updatedAt: DateTime.now().subtract(Duration(seconds: totalSeconds)),
      ),
    );
  }

  void createRandomData(int n) {
    for (var i = 0; i < n; i++) {
      final syncProfile = createRandomProfile();
      _syncProfiles[syncProfile.id] = syncProfile;
    }
  }

  void addInProgressProfile() {
    var syncProfile = createRandomProfile();
    syncProfile = syncProfile.copyWith(
      lastSuccessfulSync: DateTime.now().subtract(const Duration(days: 1)),
      status: SyncProfileStatus.inProgress(
        updatedAt: DateTime.now().subtract(const Duration(seconds: 10)),
      ),
    );
    _syncProfiles[syncProfile.id] = syncProfile;
  }

  void addFailedProfile() {
    var syncProfile = createRandomProfile();
    syncProfile = syncProfile.copyWith(
        lastSuccessfulSync: DateTime.now().subtract(const Duration(days: 1)),
        status: SyncProfileStatus.failed("Error message",
            updatedAt: DateTime.now()
                .subtract(const Duration(hours: 10, minutes: 30))));

    _syncProfiles[syncProfile.id] = syncProfile;
  }

  void addNotStartedProfile() {
    var syncProfile = createRandomProfile();
    syncProfile = syncProfile.copyWith(
      lastSuccessfulSync: null,
      status: SyncProfileStatus.notStarted(
        updatedAt: DateTime.now().subtract(const Duration(seconds: 10)),
      ),
    );

    _syncProfiles[syncProfile.id] = syncProfile;
  }

  void addDeletionFailedProfile() {
    var syncProfile = createRandomProfile();
    syncProfile = syncProfile.copyWith(
        status: SyncProfileStatus.deletionFailed("Deletion failed",
            updatedAt: DateTime.now().subtract(const Duration(seconds: 10))));

    _syncProfiles[syncProfile.id] = syncProfile;
  }

  @override
  Stream<SyncProfile?> watchSyncProfile(ID id) {
    return Stream.value(_syncProfiles[id]);
  }

  @override
  Future<void> deleteSyncProfile(ID id) async {
    _syncProfiles[id] = _syncProfiles[id]!.copyWith(
        status: SyncProfileStatus.deleting(
      updatedAt: DateTime.now(),
    ));
    _syncProfilesController.add(_syncProfiles.values.toList());
    await Future.delayed(const Duration(seconds: 2));

    _syncProfiles.remove(id);
    _syncProfilesController.add(_syncProfiles.values.toList());
  }

  /// Utility method for mock purposes, to be called when
  /// we initiate the creationg of new sync profile from the service layer.
  /// It simulates the successful creation of a new sync profile and
  /// adds it to the mock repository.
  Future<void> syncProfileCreationRequested(
      CreateSyncProfileRequest request) async {
    await Future.delayed(const Duration(milliseconds: 100)); // Simulate network

    final newId = ID();

    final createdProfile = SyncProfile(
      id: newId,
      title: request.title,
      scheduleSource: request.scheduleSource,
      targetCalendar: TargetCalendar(
        id: ID.fromString(request.targetCalendar.map(
            createNew: (c) => 'new_mock_cal_id',
            useExisting: (e) => e.calendarId)),
        title: request.targetCalendar.map(
            createNew: (c) => request.title,
            useExisting: (e) => 'Existing Mock Calendar'),
        providerAccountId: request.targetCalendar.map(
            createNew: (c) => c.providerAccountId,
            useExisting: (e) => e.providerAccountId),
        providerAccountEmail:
            'mock@example.com', // Needs to be fetched or assumed
      ),
      status: SyncProfileStatus.notStarted(updatedAt: DateTime.now()),
      lastSuccessfulSync: null,
    );
    _syncProfiles[newId] = createdProfile;
    _syncProfilesController.add(_syncProfiles.values.toList());
  }
}
