import 'package:freezed_annotation/freezed_annotation.dart';
import 'schedule_source.dart';

part 'create_sync_profile_payload.freezed.dart';
part 'create_sync_profile_payload.g.dart';

@Freezed(unionKey: 'type', unionValueCase: FreezedUnionCase.pascal)
sealed class TargetCalendarPayload with _$TargetCalendarPayload {
  const TargetCalendarPayload._();

  @FreezedUnionValue('createNew')
  const factory TargetCalendarPayload.createNew({
    @Default('createNew') String type,
    required String providerAccountId,
    int? colorId, // Google Calendar color ID (1-25)
  }) = CreateNewTargetCalendarPayload;

  @FreezedUnionValue('useExisting')
  const factory TargetCalendarPayload.useExisting({
    @Default('useExisting') String type,
    required String providerAccountId,
    required String calendarId,
  }) = UseExistingTargetCalendarPayload;

  factory TargetCalendarPayload.fromJson(Map<String, dynamic> json) =>
      _$TargetCalendarPayloadFromJson(json);
}

@freezed
class CreateSyncProfileRequest with _$CreateSyncProfileRequest {
  const factory CreateSyncProfileRequest({
    required String title,
    required ScheduleSource scheduleSource,
    required TargetCalendarPayload targetCalendar,
  }) = _CreateSyncProfileRequest;

  factory CreateSyncProfileRequest.fromJson(Map<String, dynamic> json) =>
      _$CreateSyncProfileRequestFromJson(json);
}
