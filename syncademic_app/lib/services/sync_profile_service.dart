import 'dart:developer';

enum SynchronizationType {
  regular,
  full,
}

abstract class SyncProfileService {
  Future<void> requestSync(String syncProfileId,
      {SynchronizationType synchronizationType = SynchronizationType.regular});
}

class MockSyncProfileService implements SyncProfileService {
  @override
  Future<void> requestSync(
    String syncProfileId, {
    SynchronizationType synchronizationType = SynchronizationType.regular,
  }) async {
    log('Requesting sync for $syncProfileId using a mock service (type: $synchronizationType)');
  }
}
