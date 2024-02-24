import 'dart:async';

import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:get_it/get_it.dart';
import 'package:syncademic_app/models/target_calendar.dart';
import 'package:syncademic_app/repositories/target_calendar_repository.dart';
import '../../../authorization/authorization_service.dart';

part 'target_calendar_selector_state.dart';
part 'target_calendar_selector_cubit.freezed.dart';

class TargetCalendarSelectorCubit extends Cubit<TargetCalendarSelectorState> {
  TargetCalendarSelectorCubit() : super(const TargetCalendarSelectorState());

  Future<void> authorize() async {
    emit(state.copyWith(authorizationStatus: AuthorizationStatus.authorizing));
    final isAuthorized = await GetIt.I<AuthorizationService>().authorize();

    if (!isAuthorized) {
      emit(state.copyWith(
          authorizationStatus: AuthorizationStatus.unauthorized,
          calendars: [],
          selected: null));
      return;
    }

    emit(state.copyWith(authorizationStatus: AuthorizationStatus.authorized));

    unawaited(setCalendars());
  }

  Future<void> setCalendars() async {
    final isAuthorized = await GetIt.I<AuthorizationService>().isAuthorized();

    if (!isAuthorized) {
      emit(state.copyWith(
          authorizationStatus: AuthorizationStatus.unauthorized,
          calendars: [],
          selected: null));
      return;
    }

    final calendars = await GetIt.I<TargetCalendarRepository>().getCalendars();
    emit(state.copyWith(
      authorizationStatus: AuthorizationStatus.authorized,
      calendars: calendars,
    ));
  }

  void selectCalendar(TargetCalendar? calendar) {
    emit(state.copyWith(selected: calendar));
  }
}
