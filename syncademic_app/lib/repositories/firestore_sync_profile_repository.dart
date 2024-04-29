import 'dart:developer';
import 'package:cloud_functions/cloud_functions.dart';

import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:get_it/get_it.dart';

import '../models/id.dart';
import '../models/schedule_source.dart';
import '../models/sync_profile.dart';
import '../models/sync_profile_status.dart';
import '../models/target_calendar.dart';
import '../services/auth_service.dart';
import 'sync_profile_repository.dart';

class FirestoreSyncProfileRepository implements SyncProfileRepository {
  final _db = FirebaseFirestore.instance;

  @override
  Future<void> createSyncProfile(SyncProfile syncProfile) async {
    _syncProfilesCollection.doc(syncProfile.id.value).set({
      'title': syncProfile.title,
      'scheduleSource': {
        'url': syncProfile.scheduleSource.url,
      },
      'targetCalendar': {
        'id': syncProfile.targetCalendar.id.value,
        'title': syncProfile.targetCalendar.title,
        'description': syncProfile.targetCalendar.description,
        'providerAccountId': syncProfile.targetCalendar.providerAccountId,
      },
      'status': {'type': 'notStarted'}
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
        // TODO : Handle parsing error
        return _fromData(data, doc.id);
      }).toList();
    }
  }

  SyncProfile _fromData(Map<String, dynamic> data, String id) {
    final scheduleSource = ScheduleSource(
      url: data['scheduleSource']['url'],
    );

    final targetCalendar = TargetCalendar(
      id: ID.fromString(data['targetCalendar']['id']),
      title: data['targetCalendar']['title'],
      providerAccountId: data['targetCalendar']['providerAccountId'],
      description: data['targetCalendar']['description'],
    );

    SyncProfileStatus? status; //TODO : Refactor this crap
    switch (data['status']['type']) {
      case 'inProgress':
        status = SyncProfileStatus.inProgress(
          syncTrigger: data['status']['syncTrigger'],
          lastSuccessfulSync:
              (data['status']['lastSuccessfulSync'] as Timestamp?)?.toDate(),
        );
        break;
      case 'success':
        status = SyncProfileStatus.success(
          syncTrigger: data['status']['syncTrigger'],
          lastSuccessfulSync:
              (data['status']['lastSuccessfulSync'] as Timestamp?)?.toDate(),
        );
        break;
      case 'failed':
        status = SyncProfileStatus.failed(
          data['status']['message'] ?? '',
          syncTrigger: data['status']['syncTrigger'],
          lastSuccessfulSync:
              (data['status']['lastSuccessfulSync'] as Timestamp?)?.toDate(),
        );
        break;
      case 'notStarted':
        status = SyncProfileStatus.notStarted(
          syncTrigger: data['status']['syncTrigger'],
          lastSuccessfulSync:
              (data['status']['lastSuccessfulSync'] as Timestamp?)?.toDate(),
        );
        break;
      case 'deleting':
        status = const SyncProfileStatus.deleting();
        break;
      case 'deletionFailed':
        status =
            SyncProfileStatus.deletionFailed(data['status']['message'] ?? '');
        break;
      default:
        log('Could not parse status: ${data['status']}');
    }

    return SyncProfile(
      id: ID.fromString(id),
      title: data['title'],
      scheduleSource: scheduleSource,
      targetCalendar: targetCalendar,
      status: status,
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
      FirebaseFunctions.instance.httpsCallable('delete_sync_profile').call(
        {'syncProfileId': id.value},
      );
}
