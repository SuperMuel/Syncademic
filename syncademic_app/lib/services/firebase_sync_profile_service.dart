import 'dart:developer';

import 'package:cloud_functions/cloud_functions.dart';
import 'package:syncademic_app/models/create_sync_profile_payload.dart';

import 'sync_profile_service.dart';

class FirebaseSyncProfileService implements SyncProfileService {
  @override
  Future<void> requestSync(
    String syncProfileId, {
    SynchronizationType synchronizationType = SynchronizationType.regular,
  }) async {
    log('Requesting $synchronizationType sync for $syncProfileId');
    try {
      await FirebaseFunctions.instance.httpsCallable('request_sync').call({
        'syncProfileId': syncProfileId,
        'syncType': synchronizationType.name,
      });
    } on FirebaseFunctionsException catch (e) {
      log('Error requesting sync');
      log(e.code);
      log(e.details);
      log('${e.message}');
      rethrow;
    }
  }

  @override
  Future<void> createSyncProfile(
    CreateSyncProfileRequest syncProfileRequest,
  ) async {
    log('Creating sync profile with payload: \\${syncProfileRequest.toJson()}');
    try {
      await FirebaseFunctions.instance
          .httpsCallable('create_sync_profile')
          .call(syncProfileRequest.toJson());
    } on FirebaseFunctionsException catch (e) {
      log('Error creating sync profile');
      log(e.code);
      log(e.details);
      log('\\${e.message}');
      rethrow;
    }
  }
}
