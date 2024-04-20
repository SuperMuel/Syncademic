import 'package:freezed_annotation/freezed_annotation.dart';

part 'sync_profile_status.freezed.dart';

@freezed
class SyncProfileStatus with _$SyncProfileStatus {
  const SyncProfileStatus._();

  const factory SyncProfileStatus.success({String? syncTrigger}) = _Success;
  const factory SyncProfileStatus.inProgress({String? syncTrigger}) =
      _InProgress;
  const factory SyncProfileStatus.failed(String message,
      {String? syncTrigger}) = _Failed;
  const factory SyncProfileStatus.notStarted({String? syncTrigger}) =
      _NotStarted;
}
