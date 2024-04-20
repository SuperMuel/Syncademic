import 'dart:developer';

abstract class SyncProfileService {
  Future<void> requestSync(String syncProfileId);
}

class MockSyncProfileService implements SyncProfileService {
  @override
  Future<void> requestSync(String syncProfileId) async {
    log('Requesting sync for $syncProfileId using a mock service');
  }
}
