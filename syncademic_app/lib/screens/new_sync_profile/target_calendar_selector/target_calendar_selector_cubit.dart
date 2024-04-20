import 'dart:async';

import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:get_it/get_it.dart';
import '../../../repositories/target_calendar_repository.dart';

import '../../../authorization/authorization_service.dart';
import '../../../models/target_calendar.dart';

part 'target_calendar_selector_cubit.freezed.dart';
part 'target_calendar_selector_state.dart';

class TargetCalendarSelectorCubit extends Cubit<TargetCalendarSelectorState> {
  TargetCalendarSelectorCubit() : super(const TargetCalendarSelectorState());

  //TODO : add a method that verifies if the user is authorized, and skip the authorization process if so

  Future<void> authorize() async {
    final authorizationService = GetIt.I<AuthorizationService>();

    emit(state.copyWith(authorizationStatus: AuthorizationStatus.authorizing));

    final isAuthorized = await authorizationService.authorize();

    if (!isAuthorized) {
      return emit(state.copyWith(
          authorizationStatus: AuthorizationStatus.unauthorized,
          calendars: [],
          selected: null));
    }

    emit(state.copyWith(authorizationStatus: AuthorizationStatus.authorized));

    //TODO : handle errors
    final calendars = await GetIt.I<TargetCalendarRepository>().getCalendars();

    emit(state.copyWith(calendars: calendars));
  }

  void calendarSelected(TargetCalendar? calendar) =>
      emit(state.copyWith(selected: calendar));
}
