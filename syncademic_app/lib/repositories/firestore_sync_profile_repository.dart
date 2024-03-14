import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:get_it/get_it.dart';
import '../models/target_calendar.dart';
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
      // 'title' //TODO(SuperMuel) : Implement title
      'scheduleSource': {
        'url': syncProfile.scheduleSource.url,
      },
      'targetCalendar': {
        'id': syncProfile.targetCalendar.id.value,
        'title': syncProfile.targetCalendar.title,
        'accessToken': syncProfile.targetCalendar.accessToken,
      },
    });
  }

  @override
  Stream<SyncProfile?> watchSyncProfile(ID id) {
    return _syncProfilesCollection.doc(id.value).snapshots().map((doc) {
      if (!doc.exists) {
        return null;
      }
      final data = doc.data() as Map<String, dynamic>;
      return _fromData(data, doc.id);
    });
  }

  @override
  Future<SyncProfile?> getSyncProfile(ID id) async {
    return watchSyncProfile(id).first;
  }

  @override
  Stream<List<SyncProfile>> getSyncProfiles() async* {
    await for (final snapshot in _syncProfilesCollection.snapshots()) {
      yield snapshot.docs.map((doc) {
        final data = doc.data() as Map<String, dynamic>;
        return _fromData(data, doc.id);
      }).toList();
    }
  }

  SyncProfile _fromData(Map<String, dynamic> data, String id) {
    final scheduleSource = ScheduleSource(
      url: data['scheduleSource']['url'],
    );

    final targetCalendar = TargetCalendar(
      id: ID.fromTrustedSource(data['targetCalendar']['id']),
      title: data['targetCalendar']['title'],
    );

    return SyncProfile(
      id: ID.fromTrustedSource(id),
      scheduleSource: scheduleSource,
      targetCalendar: targetCalendar,
    );
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

  @override
  Future<void> deleteSyncProfile(ID id) =>
      _syncProfilesCollection.doc(id.value).delete();
}
