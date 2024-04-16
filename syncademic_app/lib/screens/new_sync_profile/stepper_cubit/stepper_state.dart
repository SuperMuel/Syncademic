part of 'stepper_cubit.dart';

@freezed
class StepperState with _$StepperState {
  const factory StepperState({
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
  }) = _StepperState;

  const StepperState._();

  bool get canContinue {
    if (currentStep == 0) {
      return titleError == null && !isBlank(title);
    }

    if (currentStep == 1) {
      return urlError == null && !isBlank(url);
    }

    if (currentStep == 2) {
      return true; //TODO
    }

    if (currentStep == 3) {
      return true; //TODO
    }

    return false;
  }

  bool get canGoBack => currentStep > 0;
}
