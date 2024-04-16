import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:freezed_annotation/freezed_annotation.dart';

part 'stepper_state.dart';
part 'stepper_cubit.freezed.dart';

class StepperCubit extends Cubit<StepperState> {
  StepperCubit() : super(const StepperState.title());

  void next() {
    emit(state.map(
      title: (_) => const StepperState.url(),
      url: (_) => const StepperState.targetCalendar(),
      targetCalendar: (_) => const StepperState.backendAuthorization(),
      backendAuthorization: (_) => const StepperState.summary(),
      summary: (_) => const StepperState.summary(),
    ));
  }

  void previous() {
    emit(state.map(
      title: (_) => const StepperState.title(),
      url: (_) => const StepperState.title(),
      targetCalendar: (_) => const StepperState.url(),
      backendAuthorization: (_) => const StepperState.targetCalendar(),
      summary: (_) => const StepperState.backendAuthorization(),
    ));
  }
}
