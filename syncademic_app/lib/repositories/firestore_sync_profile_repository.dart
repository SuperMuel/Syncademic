import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:get_it/get_it.dart';
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
        final data = doc.data();
        final scheduleSource = ScheduleSource(
          url: (data as Map<String, dynamic>)['scheduleSource']['url'],
        );
        return SyncProfile(
          id: ID.fromTrustedSource(doc.id),
          scheduleSource: scheduleSource,
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
