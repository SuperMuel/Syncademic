import 'package:freezed_annotation/freezed_annotation.dart';

import 'id.dart';
import 'schedule_source.dart';
import 'sync_profile_status.dart';
import 'target_calendar.dart';

part 'sync_profile.freezed.dart';

@freezed
class SyncProfile with _$SyncProfile {
  const factory SyncProfile({
    required ID id,
    required ScheduleSource scheduleSource,
    required TargetCalendar targetCalendar,
    required String title,
    @Default(false) bool enabled,
    DateTime? lastSuccessfulSync,
    SyncProfileStatus? status,
  }) = _SyncProfile;
}
