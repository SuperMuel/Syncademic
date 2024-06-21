part of 'sync_profile_cubit.dart';

@freezed
class SyncProfileState with _$SyncProfileState {
  const factory SyncProfileState.loading() = _Loading;
  const factory SyncProfileState.loaded(
    SyncProfile syncProfile, {
    String? requestSyncError,
    DateTime? lastSyncRequest,
    @Default(false) bool confirmingDeletion,
    @Default(false) bool isDeleting,
    String? deletionError,
  }) = _Loaded;
  const factory SyncProfileState.notFound() = _NotFound;
  const factory SyncProfileState.deleted() = _Deleted;

  const SyncProfileState._();

  /// Minimum interval between synchronization requests.
  static const kMinSyncInterval = Duration(minutes: 5);

  /// Returns true if the synchronization isn't already in progress and the last
  /// synchronization request was made at least [kMinSyncInterval] ago.
  bool get canRequestSync => maybeMap(
        orElse: () => false,
        loaded: (loaded) {
          final profile = loaded.syncProfile;

          final isInProgress = profile.status?.isInProgress() ?? false;

          if (isInProgress) {
            // Synchronization is already in progress
            return false;
          }
          final lastSyncRequest = loaded.lastSyncRequest;
          if (lastSyncRequest == null) {
            return true;
          }

          final diff = DateTime.now().difference(lastSyncRequest);

          return diff >= kMinSyncInterval;
        },
      );

  bool get canDelete => maybeMap(
        orElse: () => false,
        loaded: (loaded) => !loaded.isDeleting,
      );
}
