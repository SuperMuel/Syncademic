part of 'new_sync_profile_cubit.dart';

enum TargetCalendarChoice { createNew, useExisting }

enum NewSyncProfileStep {
  title,
  url,
  selectProviderAccount,
  authorizeBackend,
  selectTargetCalendar,
  summary;

  NewSyncProfileStep get next {
    return NewSyncProfileStep.values[index + 1];
  }

  NewSyncProfileStep get previous {
    return NewSyncProfileStep.values[index - 1];
  }
}

enum BackendAuthorizationStatus {
  checking,
  notAuthorized,
  authorizing,
  authorized
}

@freezed
class NewSyncProfileState with _$NewSyncProfileState {
  const factory NewSyncProfileState({
    @Default(NewSyncProfileStep.title) NewSyncProfileStep currentStep,
    @Default('') String title,
    String? titleError,
    @Default('') String url,
    String? urlError,
    ProviderAccount? providerAccount,
    @Default(null) String? providerAccountError,
    TargetCalendar? existingCalendarSelected,
    TargetCalendar? newCalendarCreated,
    @Default(BackendAuthorizationStatus.notAuthorized)
    BackendAuthorizationStatus backendAuthorizationStatus,
    String? backendAuthorizationError,
    @Default(TargetCalendarChoice.createNew)
    TargetCalendarChoice targetCalendarChoice,
    @Default(GoogleCalendarColor.blue) GoogleCalendarColor targetCalendarColor,
    @Default(false) bool isSubmitting,
    String? submitError,
    @Default(false) bool submittedSuccessfully,
  }) = _NewSyncProfileState;

  const NewSyncProfileState._();

  bool get canContinue => switch (currentStep) {
        NewSyncProfileStep.title => titleError == null && !isBlank(title),
        NewSyncProfileStep.url => urlError == null && !isBlank(url),
        NewSyncProfileStep.selectProviderAccount => providerAccount != null,
        NewSyncProfileStep.selectTargetCalendar =>
          targetCalendarSelected != null,
        NewSyncProfileStep.authorizeBackend =>
          backendAuthorizationStatus == BackendAuthorizationStatus.authorized,
        NewSyncProfileStep.summary => false,
      };

  bool get canGoBack => currentStep.index > 0;

  /// The target calendar that the user has selected.
  ///
  /// If the user has selected to create a new calendar, this will be the new calendar.
  /// If the user has selected to use an existing calendar, this will be the existing calendar.
  TargetCalendar? get targetCalendarSelected {
    switch (targetCalendarChoice) {
      case TargetCalendarChoice.createNew:
        return newCalendarCreated;
      case TargetCalendarChoice.useExisting:
        return existingCalendarSelected;
    }
  }

  bool get isUrlValid => urlError == null && !isBlank(url);

  bool get isTitleValid => titleError == null && !isBlank(title);

  bool canSubmit() {
    if (!isTitleValid || !isUrlValid) {
      return false;
    }

    if (providerAccount == null) {
      return false;
    }

    if (backendAuthorizationStatus != BackendAuthorizationStatus.authorized) {
      return false;
    }

    if (targetCalendarSelected == null) {
      return false;
    }

    return true;
  }
}
