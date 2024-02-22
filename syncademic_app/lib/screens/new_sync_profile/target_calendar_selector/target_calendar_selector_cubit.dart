import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:get_it/get_it.dart';
import '../../../authorization/authorization_service.dart';

part 'target_calendar_selector_state.dart';
part 'target_calendar_selector_cubit.freezed.dart';

class TargetCalendarSelectorCubit extends Cubit<TargetCalendarSelectorState> {
  TargetCalendarSelectorCubit()
      : super(const TargetCalendarSelectorState.unauthorized());

  Future<void> authorize() async {
    emit(const TargetCalendarSelectorState.authorizing());
    final authorized = await GetIt.I<AuthorizationService>().authorize();

    emit(authorized
        ? const TargetCalendarSelectorState.authorized()
        : const TargetCalendarSelectorState.unauthorized());
  }
}
