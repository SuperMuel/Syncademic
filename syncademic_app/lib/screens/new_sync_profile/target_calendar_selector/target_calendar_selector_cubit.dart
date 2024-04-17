import 'dart:async';

import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:get_it/get_it.dart';

import '../../../authorization/authorization_service.dart';
import '../../../models/target_calendar.dart';
import '../../../repositories/google_target_calendar_repository.dart';

part 'target_calendar_selector_cubit.freezed.dart';
part 'target_calendar_selector_state.dart';

class TargetCalendarSelectorCubit extends Cubit<TargetCalendarSelectorState> {
  TargetCalendarSelectorCubit() : super(const TargetCalendarSelectorState());

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

    final authorizedClient = await authorizationService.authorizedClient;

    if (authorizedClient == null) {
      throw Exception(
          'authorizedClient is null while authorizationStatus is authorized');
    }

    final accessToken = await authorizationService.accessToken;
    if (accessToken == null) {
      throw Exception(
          'accessToken is null while authorizationStatus is authorized');
    }

    emit(state.copyWith(authorizationStatus: AuthorizationStatus.authorized));

    final calendars = await GoogleTargetCalendarRepository(
      authorizedClient: authorizedClient,
      accountOwnerUserId: await authorizationService.userId,
    ).getCalendars();

    emit(state.copyWith(calendars: calendars));
  }

  void calendarSelected(TargetCalendar? calendar) =>
      emit(state.copyWith(selected: calendar));
}
