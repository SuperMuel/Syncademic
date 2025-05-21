import 'dart:developer';

import 'package:cloud_functions/cloud_functions.dart';
import 'package:get_it/get_it.dart';
import 'package:syncademic_app/models/create_sync_profile_payload.dart';

import 'api_client.dart'; // Added import for ApiClient
import 'sync_profile_service.dart';

class FirebaseSyncProfileService implements SyncProfileService {
  final FirebaseFunctions functions;
  final ApiClient? apiClient; // Replaced fastApiBaseUrl with apiClient

  // TODO: These flags would be controlled by a configuration service or environment variables in a real app.
  final bool _useFastApiForRequestSync = false; // Keep false for now
  final bool _useFastApiForCreateProfile = false; // Keep false for now

  FirebaseSyncProfileService({
    FirebaseFunctions? functions,
    this.apiClient, // Added apiClient parameter
  }) : functions = functions ?? GetIt.I.get<FirebaseFunctions>();

  @override
  Future<void> requestSync(
    String syncProfileId, {
    SynchronizationType synchronizationType = SynchronizationType.regular,
  }) async {
    if (apiClient != null && _useFastApiForRequestSync) {
      // FastAPI path (currently inactive)
      log('Attempting to use FastAPI for requestSync (currently inactive)');
      // TODO: Implement FastAPI call when endpoint is ready
      // try {
      //   await apiClient!.post('request-sync', { // Or the correct path e.g. 'sync-profiles/$syncProfileId/request-sync'
      //     'syncProfileId': syncProfileId, // Or pass in path
      //     'syncType': synchronizationType.name,
      //   });
      //   log('Successfully requested sync via FastAPI for $syncProfileId');
      // } on ApiException catch (e) {
      //   log('Error requesting sync via FastAPI: ${e.message}');
      //   rethrow; // Or handle differently
      // }
      // For now, falling through to Cloud Function if TODO is not implemented or flag is false.
      // To strictly separate, you might `return;` here if the TODO block were live.
      // However, the requirement is to keep CF as the current path.
      // The current structure will execute the CF path because the flag is false.
      log('FastAPI path for requestSync is defined but inactive. Falling back to Cloud Function.');
    }

    // Cloud Function path (current active path)
    log('Requesting $synchronizationType sync for $syncProfileId via Cloud Function');
    try {
      await functions.httpsCallable('request_sync').call({
        'syncProfileId': syncProfileId,
        'syncType': synchronizationType.name,
      });
      log('Successfully requested sync via Cloud Function for $syncProfileId');
    } on FirebaseFunctionsException catch (e) {
      log('Error requesting sync via Cloud Function');
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
    if (apiClient != null && _useFastApiForCreateProfile) {
      // FastAPI path (currently inactive)
      log('Attempting to use FastAPI for createSyncProfile (currently inactive)');
      // TODO: Implement FastAPI call when endpoint is ready
      // try {
      //   await apiClient!.post('sync-profiles', syncProfileRequest.toJson()); // Or '/create-sync-profile'
      //   log('Successfully created sync profile via FastAPI');
      // } on ApiException catch (e) {
      //   log('Error creating sync profile via FastAPI: ${e.message}');
      //   rethrow; // Or handle differently
      // }
      log('FastAPI path for createSyncProfile is defined but inactive. Falling back to Cloud Function.');
    }

    // Cloud Function path (current active path)
    log('Creating sync profile via Cloud Function with payload: ${syncProfileRequest.toJson()}');
    try {
      await functions
          .httpsCallable('create_sync_profile')
          .call(syncProfileRequest.toJson());
      log('Successfully created sync profile via Cloud Function');
    } on FirebaseFunctionsException catch (e) {
      log('Error creating sync profile via Cloud Function');
      log(e.code);
      log(e.details);
      log('${e.message}');
      rethrow;
    }
  }
}
