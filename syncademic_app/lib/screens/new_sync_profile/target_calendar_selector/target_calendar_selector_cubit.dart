import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:get_it/get_it.dart';
import 'package:syncademic_app/models/provider_account.dart';

import '../../../models/target_calendar.dart';
import '../../../repositories/target_calendar_repository.dart';

part 'target_calendar_selector_cubit.freezed.dart';
part 'target_calendar_selector_state.dart';

class TargetCalendarSelectorCubit extends Cubit<TargetCalendarSelectorState> {
  TargetCalendarSelectorCubit(this.providerAccount)
      : super(const TargetCalendarSelectorState());

  final ProviderAccount providerAccount;

  void init() async {
    emit(state.copyWith(loading: true));

    late List<TargetCalendar> calendars;
    try {
      calendars = await GetIt.I.get<TargetCalendarRepository>().getCalendars(
            providerAccount.id.toString(),
          );
    } catch (e) {
      emit(state.copyWith(loading: false, error: e.toString()));
    }

    emit(state.copyWith(loading: false, calendars: calendars, error: null));
  }

  void calendarSelected(TargetCalendar? calendar) =>
      emit(state.copyWith(selected: calendar));
}
