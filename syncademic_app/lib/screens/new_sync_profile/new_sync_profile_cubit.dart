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

    if (url.length > 500) {
      return emit(state.copyWith(url: url, urlError: 'URL is too long'));
    }

    if (!isURL(url)) {
      return emit(state.copyWith(url: url, urlError: 'URL is not valid'));
    }

    emit(state.copyWith(url: url, urlError: null));
  }

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

  Future<void> submit() async {
    if (state.hasError ||
        state.selectedCalendar == null ||
        state.title.isEmpty) {
      throw StateError('Cannot submit with invalid data');
    }
    emit(state.copyWith(isSubmitting: true));

    final scheduleSource = ScheduleSource(
      url: state.url,
    );

    final syncProfile = SyncProfile(
      id: ID(),
      title: state.title,
      scheduleSource: scheduleSource,
      targetCalendar: state.selectedCalendar!,
    );

    final repo = GetIt.I<SyncProfileRepository>();

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
