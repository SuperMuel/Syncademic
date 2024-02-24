import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:get_it/get_it.dart';
import 'package:syncademic_app/models/target_calendar.dart';
import '../models/id.dart';
import '../models/schedule_source.dart';
import '../models/sync_profile.dart';
import 'sync_profile_repository.dart';
import '../services/auth_service.dart';

class FirestoreSyncProfileRepository implements SyncProfileRepository {
  final _db = FirebaseFirestore.instance;

  @override
  Future<void> createSyncProfile(SyncProfile syncProfile) async {
    _syncProfilesCollection.doc(syncProfile.id.value).set({
      'scheduleSource': {
        'url': syncProfile.scheduleSource.url,
      },
    });
  }

  @override
  Future<SyncProfile?> getSyncProfile(ID id) async {
    // TODO: implement getSyncProfile
    throw UnimplementedError();
  }

  @override
  Stream<List<SyncProfile>> getSyncProfiles() async* {
    await for (final snapshot in _syncProfilesCollection.snapshots()) {
      yield snapshot.docs.map((doc) {
        final data = doc.data() as Map<String, dynamic>;
        final scheduleSource = ScheduleSource(
          url: data['scheduleSource']['url'],
        );

        // TODO: Replace with real target calendar
        const targetCalendar = TargetCalendar(
          id: ID.fromTrustedSource('target-google-calendar-0'),
          title: 'Calendar 0',
        );

        return SyncProfile(
          id: ID.fromTrustedSource(doc.id),
          scheduleSource: scheduleSource,
          targetCalendar: targetCalendar,
        );
      }).toList();
    }
  }

  @override
  Future<void> updateSyncProfile(SyncProfile syncProfile) {
    // TODO: implement updateSyncProfile
    throw UnimplementedError();
  }

  CollectionReference get _syncProfilesCollection {
    final user = GetIt.I<AuthService>().currentUser;
    if (user == null) {
      throw Exception('User not signed in');
    }
    return _db.collection('users').doc(user.id).collection('syncProfiles');
  }
}
