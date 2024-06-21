part of 'sync_profile_2_cubit.dart';

@freezed
class SyncProfile_2State with _$SyncProfile_2State {
  const factory SyncProfile_2State({
    required SyncProfile syncProfile,
    @Default(false) bool canRequestSync,
  }) = _SyncProfile_2State;

  const SyncProfile_2State._();

  /// Minimum interval between synchronization requests.
  static const kMinSyncInterval = Duration(minutes: 5);

  /// Returns true if the synchronization isn't already in progress and the last
  /// synchronization request was made at least [kMinSyncInterval] ago.
  bool get canRequestSync {
    return false;
  }

  bool get canRequestDeletion {
    return false;
  }

  // => maybeMap(
  //       orElse: () => false,
  //       loaded: (loaded) {
  //         final profile = loaded.syncProfile;

  //         final isInProgress = profile.status?.isInProgress() ?? false;

  //         if (isInProgress) {
  //           // Synchronization is already in progress
  //           return false;
  //         }
  //         final lastSyncRequest = loaded.lastSyncRequest;
  //         if (lastSyncRequest == null) {
  //           return true;
  //         }

  //         final diff = DateTime.now().difference(lastSyncRequest);

  //         return diff >= kMinSyncInterval;
  //       },
  //     );
}
