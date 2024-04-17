part of 'new_sync_profile_cubit.dart';

@freezed
class NewSyncProfileState with _$NewSyncProfileState {
  const factory NewSyncProfileState({
    @Default(0) int currentStep,
    @Default('') String title,
    String? titleError,
    @Default('') String url,
    String? urlError,
    TargetCalendar? targetCalendar,
    String? backendAuthorization,
    @Default(false) bool isSubmitting,
    String? submitError,
    @Default(false) bool submittedSuccessfully,
  }) = _NewSyncProfileState;

  const NewSyncProfileState._();

  bool get canContinue {
    if (currentStep == 0) {
      return titleError == null && !isBlank(title);
    }

    if (currentStep == 1) {
      return urlError == null && !isBlank(url);
    }

    if (currentStep == 2) {
      return targetCalendar != null;
    }

    if (currentStep == 3) {
      return true; //TODO
    }

    return false;
  }

  bool get canGoBack => currentStep > 0;
}
