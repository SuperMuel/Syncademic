part of 'target_calendar_selector_cubit.dart';

enum AuthorizationStatus { unauthorized, authorizing, authorized }

@freezed
class TargetCalendarSelectorState with _$TargetCalendarSelectorState {
  const factory TargetCalendarSelectorState({
    @Default(AuthorizationStatus.unauthorized)
    AuthorizationStatus authorizationStatus,
    @Default([]) List<TargetCalendar> calendars,
    TargetCalendar? selected,
  }) = _TargetCalendarSelectorState;
}
