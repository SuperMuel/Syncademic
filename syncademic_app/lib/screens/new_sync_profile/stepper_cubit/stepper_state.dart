part of 'stepper_cubit.dart';

@freezed
class StepperState with _$StepperState {
  const factory StepperState({
    @Default(0) int currentStep,
    @Default('') String title,
    String? titleError,
    @Default('') String url,
    String? urlError,
    @Default(null) TargetCalendar? selectedCalendar,
    @Default(null) String? backendAuthorization,
  }) = _StepperState;

  const StepperState._();

  bool get canContinue {
    if (currentStep == 0) {
      print(
          'StepperState: canContinue: titleError: $titleError, title: $title');
      print("Title error : $titleError");
      print("Title : $title");
      print("isBlank(title) : ${isBlank(title)}");
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
