import 'package:freezed_annotation/freezed_annotation.dart';

part 'sync_profile_status.freezed.dart';

@freezed
class SyncProfileStatus with _$SyncProfileStatus {
  const SyncProfileStatus._();

  const factory SyncProfileStatus.success({String? syncTrigger, DateTime? lastSuccessfulSync}) = _Success;
  const factory SyncProfileStatus.inProgress({String? syncTrigger, DateTime? lastSuccessfulSync}) = _InProgress;
  const factory SyncProfileStatus.failed(String message, {String? syncTrigger, DateTime? lastSuccessfulSync}) = _Failed;
  const factory SyncProfileStatus.notStarted({String? syncTrigger, DateTime? lastSuccessfulSync}) = _NotStarted;

  bool isInProgress() => maybeMap(
        orElse: () => false,
        inProgress: (_) => true,
      );
}
