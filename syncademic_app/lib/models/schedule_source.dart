import 'package:freezed_annotation/freezed_annotation.dart';

part 'schedule_source.freezed.dart';
part 'schedule_source.g.dart';

@freezed
class ScheduleSource with _$ScheduleSource {
  const factory ScheduleSource({
    required String url,
  }) = _ScheduleSource;

  factory ScheduleSource.fromJson(Map<String, dynamic> json) =>
      _$ScheduleSourceFromJson(json);
}
