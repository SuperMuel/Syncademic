import 'dart:developer';

import 'package:syncademic_app/models/create_sync_profile_payload.dart';
import 'package:syncademic_app/repositories/sync_profile_repository.dart';

enum SynchronizationType {
  regular,
  full,
}

abstract class SyncProfileService {
  Future<void> requestSync(String syncProfileId,
      {SynchronizationType synchronizationType = SynchronizationType.regular});
  Future<void> createSyncProfile(CreateSyncProfileRequest syncProfileRequest);
}

class MockSyncProfileService implements SyncProfileService {
  final MockSyncProfileRepository repository;

  MockSyncProfileService(this.repository);

  @override
  Future<void> requestSync(
    String syncProfileId, {
    SynchronizationType synchronizationType = SynchronizationType.regular,
  }) async {
    log('Requesting sync for $syncProfileId using a mock service (type: $synchronizationType)');
  }

  @override
  Future<void> createSyncProfile(
      CreateSyncProfileRequest syncProfileRequest) async {
    log('Creating sync profile for ${syncProfileRequest.title} using a mock service');
    await repository.syncProfileCreationRequested(syncProfileRequest);
  }
}
