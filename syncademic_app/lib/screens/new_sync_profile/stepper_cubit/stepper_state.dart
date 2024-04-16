part of 'stepper_cubit.dart';

@freezed
class StepperState with _$StepperState {
  const factory StepperState.title({@Default('') String title, String? error}) =
      _Title;

  const factory StepperState.url() = _Url;
  const factory StepperState.targetCalendar() = _TargetCalendar;
  const factory StepperState.backendAuthorization() = _BackendAuthorization;
  const factory StepperState.summary() = _Summary;

  const StepperState._();

  bool get isValid {
    return when(
      title: (title, error) => error == null,
      url: () => true,
      targetCalendar: () => true,
      backendAuthorization: () => true,
      summary: () => true,
    );
  }

  /// Returns the index of the current state in the stepper.
  ///
  /// Starting from 0.
  int get index {
    return when(
      title: (_, __) => 0,
      url: () => 1,
      targetCalendar: () => 2,
      backendAuthorization: () => 3,
      summary: () => 4,
    );
  }

  bool get canCancel {
    return maybeWhen(
      title: (_, __) => false,
      orElse: () => true,
    );
  }

  bool get canContinue {
    return map(
      title: (state) => state.isValid,
      url: (_) => true,
      targetCalendar: (_) => true,
      backendAuthorization: (_) => true,
      summary: (_) => true,
    );
  }
}
