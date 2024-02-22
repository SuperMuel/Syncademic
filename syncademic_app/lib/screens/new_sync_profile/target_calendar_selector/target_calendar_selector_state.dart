part of 'target_calendar_selector_cubit.dart';

@freezed
class TargetCalendarSelectorState with _$TargetCalendarSelectorState {
  const factory TargetCalendarSelectorState.unauthorized() = _Unauthorized;
  const factory TargetCalendarSelectorState.authorizing() = _Authorizing;
  const factory TargetCalendarSelectorState.authorized() = _Authorized;
}
