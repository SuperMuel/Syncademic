import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:get_it/get_it.dart';
import 'package:quiver/strings.dart';
import 'package:validators/validators.dart';

import '../../models/id.dart';
import '../../models/schedule_source.dart';
import '../../models/sync_profile.dart';
import '../../models/target_calendar.dart';
import '../../models/types.dart';
import '../../repositories/sync_profile_repository.dart';

part 'new_sync_profile_cubit.freezed.dart';
part 'new_sync_profile_state.dart';

class NewSyncProfileCubit extends Cubit<NewSyncProfileState> {
  NewSyncProfileCubit() : super(const NewSyncProfileState(url: ''));

  void urlChanged(Url url) {
    if (isBlank(url)) {
      return emit(state.copyWith(url: url, urlError: 'URL cannot be empty'));
    }

    if (url.length > 5000) {
      return emit(state.copyWith(url: url, urlError: 'URL is too long'));
    }

    if (!isURL(url)) {
      return emit(state.copyWith(url: url, urlError: 'URL is not valid'));
    }

    emit(state.copyWith(url: url, urlError: null));
  }

  Future<void> submit() async {
    if (state.urlError != null || state.selectedCalendar == null) {
      throw StateError('Cannot submit with invalid data');
    }
    emit(state.copyWith(isSubmitting: true));

    final repo = GetIt.I<SyncProfileRepository>();

    final scheduleSource = ScheduleSource(
      url: state.url,
    );
    final syncProfile = SyncProfile(
      id: ID(),
      scheduleSource: scheduleSource,
      targetCalendar: state.selectedCalendar!,
    );

    try {
      await repo.createSyncProfile(syncProfile);
      emit(state.copyWith(isSuccess: true));
    } catch (e) {
      emit(state.copyWith(errorMessage: e.toString()));
    }
  }

  void calendarSelected(TargetCalendar? calendar) {
    emit(state.copyWith(selectedCalendar: calendar));
  }
}
