import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:quiver/strings.dart';
import 'package:syncademic_app/models/target_calendar.dart';
import 'package:validators/validators.dart';

part 'stepper_state.dart';
part 'stepper_cubit.freezed.dart';

class StepperCubit extends Cubit<StepperState> {
  StepperCubit() : super(const StepperState());

  void titleChanged(String title) {
    if (isBlank(title)) {
      return emit(
          state.copyWith(title: title, titleError: 'Title cannot be empty'));
    }

    if (title.length > 50) {
      return emit(
          state.copyWith(title: title, titleError: 'Title is too long'));
    }

    emit(state.copyWith(title: title, titleError: null));
  }

  void urlChanged(String url) {
    if (isBlank(url)) {
      return emit(state.copyWith(url: url, urlError: 'URL cannot be empty'));
    }

    // URLs from Montpellier Fds are 400+ characters long. We need to support
    // long URLs.
    if (url.length > 2000) {
      return emit(state.copyWith(url: url, urlError: 'URL is too long'));
    }

    if (!isURL(url)) {
      return emit(state.copyWith(url: url, urlError: 'URL is not valid'));
    }

    emit(state.copyWith(url: url, urlError: null));
  }

  void selectCalendar(TargetCalendar? calendar) {
    if (calendar == null) {
      return;
    }
    emit(state.copyWith(targetCalendar: calendar));
  }

  void backendAuthorizationChanged(String backendAuthorization) {
    emit(state.copyWith(backendAuthorization: backendAuthorization));
  }

  void next() {
    if (state.canContinue) {
      emit(state.copyWith(currentStep: state.currentStep + 1));
    } else {
      print('StepperCubit: next: cannot continue');
    }
  }

  void previous() {
    if (state.canGoBack) {
      emit(state.copyWith(currentStep: state.currentStep - 1));
    }
  }
}
