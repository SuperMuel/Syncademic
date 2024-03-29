import 'package:freezed_annotation/freezed_annotation.dart';

part 'sync_profile_status.freezed.dart';

@freezed
class SyncProfileStatus with _$SyncProfileStatus {
  const SyncProfileStatus._();

  const factory SyncProfileStatus.success() = _Success;
  const factory SyncProfileStatus.inProgress() = _InProgress;
  const factory SyncProfileStatus.failed(String message) = _Failed;
  const factory SyncProfileStatus.notStarted() = _NotStarted;
}
