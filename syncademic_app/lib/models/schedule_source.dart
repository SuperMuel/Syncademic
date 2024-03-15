import 'package:freezed_annotation/freezed_annotation.dart';

part 'schedule_source.freezed.dart';

@freezed
class ScheduleSource with _$ScheduleSource {
  const factory ScheduleSource({
    required String url,
  }) = _ScheduleSource;
}
