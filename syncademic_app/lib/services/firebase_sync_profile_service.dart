import 'dart:developer';

import 'package:cloud_functions/cloud_functions.dart';
import 'package:get_it/get_it.dart';
import 'package:syncademic_app/models/create_sync_profile_payload.dart';

import 'sync_profile_service.dart';

class FirebaseSyncProfileService implements SyncProfileService {
  final FirebaseFunctions functions;

  FirebaseSyncProfileService({FirebaseFunctions? functions})
      : functions = functions ?? GetIt.I.get<FirebaseFunctions>();

  @override
  Future<void> requestSync(
    String syncProfileId, {
    SynchronizationType synchronizationType = SynchronizationType.regular,
  }) async {
    log('Requesting $synchronizationType sync for $syncProfileId');
    try {
      await functions.httpsCallable('request_sync').call({
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
      await functions
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
