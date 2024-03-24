import 'package:freezed_annotation/freezed_annotation.dart';

import 'id.dart';

part 'target_calendar.freezed.dart';

@freezed
class TargetCalendar with _$TargetCalendar {
  const factory TargetCalendar({
    required ID id,
    required String title,
    String? accessToken,
  }) = _TargetCalendar;
}
