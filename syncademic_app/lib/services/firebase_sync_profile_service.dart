import 'dart:developer';

import 'package:cloud_functions/cloud_functions.dart';
import 'sync_profile_service.dart';

class FirebaseSyncProfileService implements SyncProfileService {
  @override
  Future<void> requestSync(String syncProfileId) async {
    log('Requesting sync for $syncProfileId');
    try {
      await FirebaseFunctions.instance.httpsCallable('request_sync').call({
        'syncProfileId': syncProfileId,
      });
    } on FirebaseFunctionsException catch (e) {
      log('Error requesting sync');
      log(e.code);
      log(e.details);
      log('${e.message}');
      rethrow;
    }
  }
}
