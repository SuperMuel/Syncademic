part of 'target_calendar_selector_cubit.dart';

@freezed
class TargetCalendarSelectorState with _$TargetCalendarSelectorState {
  const factory TargetCalendarSelectorState({
    @Default(true) loading,
    String? error,
    @Default([]) List<TargetCalendar> calendars,
    TargetCalendar? selected,
  }) = _TargetCalendarSelectorState;
}
