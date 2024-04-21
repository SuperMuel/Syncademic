part of 'new_sync_profile_cubit.dart';

enum TargetCalendarChoice { createNew, useExisting }

@freezed
class NewSyncProfileState with _$NewSyncProfileState {
  const factory NewSyncProfileState({
    @Default(0) int currentStep,
    @Default('') String title,
    String? titleError,
    @Default('') String url,
    String? urlError,
    TargetCalendar? targetCalendar,
    @Default(TargetCalendarChoice.createNew)
    TargetCalendarChoice targetCalendarChoice,
    @Default(false) bool isAuthorizingBackend,
    @Default(false) bool hasAuthorizedBackend,
    String? backendAuthorizationError,
    @Default(false) bool isSubmitting,
    String? submitError,
    @Default(false) bool submittedSuccessfully,
  }) = _NewSyncProfileState;

  const NewSyncProfileState._();

  bool get canContinue {
    // Step 0: Title
    if (currentStep == 0) {
      return titleError == null && !isBlank(title);
    }

    // Step 1: URL
    if (currentStep == 1) {
      return urlError == null && !isBlank(url);
    }

    // Step 2: Target calendar
    if (currentStep == 2) {
      return targetCalendar != null;
    }

    // Step 3: Authorize backend
    if (currentStep == 3) {
      return hasAuthorizedBackend;
    }

    return false;
  }

  bool get canGoBack => currentStep > 0;
}
