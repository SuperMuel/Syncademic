part of 'stepper_cubit.dart';

@freezed
class StepperState with _$StepperState {
  const factory StepperState.title() = _Title;
  const factory StepperState.url() = _Url;
  const factory StepperState.targetCalendar() = _TargetCalendar;
  const factory StepperState.backendAuthorization() = _BackendAuthorization;
  const factory StepperState.summary() = _Summary;

  const StepperState._();

  /// Returns the index of the current state in the stepper.
  ///
  /// Starting from 0.
  int get index {
    return when(
      title: () => 0,
      url: () => 1,
      targetCalendar: () => 2,
      backendAuthorization: () => 3,
      summary: () => 4,
    );
  }

  bool get canCancel {
    return maybeWhen(
      title: () => false,
      orElse: () => true,
    );
  }

  bool get canContinue {
    return maybeWhen(
      summary: () => false,
      orElse: () => true,
    );
  }
}
