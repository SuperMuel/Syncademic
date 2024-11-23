import 'package:freezed_annotation/freezed_annotation.dart';

part 'sync_profile_status.freezed.dart';

@freezed
class SyncProfileStatus with _$SyncProfileStatus {
  const SyncProfileStatus._();

  const factory SyncProfileStatus.success({
    String? syncTrigger,
    required DateTime updatedAt,
  }) = _Success;
  const factory SyncProfileStatus.inProgress({
    String? syncTrigger,
    required DateTime updatedAt,
  }) = _InProgress;
  const factory SyncProfileStatus.failed(
    String message, {
    String? syncTrigger,
    required DateTime updatedAt,
  }) = _Failed;
  const factory SyncProfileStatus.notStarted({
    String? syncTrigger,
    required DateTime updatedAt,
  }) = _NotStarted;
  const factory SyncProfileStatus.deleting({
    required DateTime updatedAt,
  }) = _Deleting;
  const factory SyncProfileStatus.deletionFailed(
    String message, {
    required DateTime updatedAt,
  }) = _DeletionFailed;

  bool isInProgress() => maybeMap(
        orElse: () => false,
        inProgress: (_) => true,
      );
}
