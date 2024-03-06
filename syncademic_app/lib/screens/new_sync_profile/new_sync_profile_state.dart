part of 'new_sync_profile_cubit.dart';

@freezed
class NewSyncProfileState with _$NewSyncProfileState {
  const NewSyncProfileState._();

  const factory NewSyncProfileState({
    @Default('') Url url,
    @Default(null) String? urlError,
    @Default(false) bool isSubmitting,
    @Default(false) bool isSuccess,
    @Default(null) String? errorMessage,
    @Default(null) TargetCalendar? selectedCalendar,
  }) = _NewSyncProfileState;

  bool get canSubmit =>
      url.isNotEmpty &&
      urlError == null &&
      selectedCalendar != null &&
      !isSubmitting;

  bool get canEditUrl => !isSubmitting;
}
