import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:get_it/get_it.dart';
import 'package:quiver/strings.dart';
import '../../../authorization/backend_authorization_service.dart';
import '../../../models/id.dart';
import '../../../models/schedule_source.dart';
import '../../../models/sync_profile.dart';
import '../../../models/target_calendar.dart';
import '../../../repositories/sync_profile_repository.dart';
import 'package:validators/validators.dart';

part 'new_sync_profile_state.dart';
part 'new_sync_profile_cubit.freezed.dart';

class NewSyncProfileCubit extends Cubit<NewSyncProfileState> {
  NewSyncProfileCubit() : super(const NewSyncProfileState());

  void titleChanged(String title) {
    if (isBlank(title)) {
      return emit(
          state.copyWith(title: title, titleError: 'Title cannot be empty'));
    }

    if (title.length > 50) {
      return emit(
          state.copyWith(title: title, titleError: 'Title is too long'));
    }

    emit(state.copyWith(
      title: title,
      titleError: null,
      newCalendarCreated: TargetCalendar(
        id: ID(),
        title: title,
        providerAccountId: '',
        createdBySyncademic: true,
        description: "Calendar created by Syncademic.io}",
      ),
    ));
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

  void targetCalendarChoiceChanged(Set<TargetCalendarChoice> choice) {
    if (choice.length != 1) {
      throw ArgumentError('Exactly one choice must be selected');
    }
    emit(state.copyWith(targetCalendarChoice: choice.first));
  }

  void selectCalendar(TargetCalendar? calendar) {
    if (calendar == null) {
      return;
    }
    emit(state.copyWith(existingCalendarSelected: calendar));
  }

  void authorizeBackend() async {
    //TODO : in this step, retrieve the user's providerAccountId in case we need it to create a new calendar.
    emit(state.copyWith(
        isAuthorizingBackend: true,
        backendAuthorizationError: null,
        hasAuthorizedBackend: false));

    try {
      await GetIt.I<BackendAuthorizationService>().authorizeBackend();
    } catch (e) {
      emit(state.copyWith(
        isAuthorizingBackend: false,
        hasAuthorizedBackend: false,
        backendAuthorizationError: e.toString(),
      ));
      return;
    }

    //TODO : check if providerAccountId is valid
    emit(state.copyWith(
      isAuthorizingBackend: false,
      hasAuthorizedBackend: true,
      backendAuthorizationError: null,
    ));
  }

  void next() {
    if (state.canContinue) {
      emit(state.copyWith(currentStep: state.currentStep + 1));
    }
  }

  void previous() {
    if (state.canGoBack) {
      emit(state.copyWith(currentStep: state.currentStep - 1));
    }
  }

  Future<void> submit() async {
    //TODO : extract this to a separate method
    if (isBlank(state.title) ||
        isBlank(state.url) ||
        (state.targetCalendarChoice == TargetCalendarChoice.useExisting &&
            state.existingCalendarSelected == null) ||
        (state.targetCalendarChoice == TargetCalendarChoice.createNew &&
            state.newCalendarCreated == null) ||
        state.titleError != null ||
        state.urlError != null) {
      throw StateError('Cannot submit with invalid data');
    }

    emit(state.copyWith(isSubmitting: true));

    //TODO : try to create new calendar if targetCalendarChoice is createNew

    final scheduleSource = ScheduleSource(
      url: state.url,
    );

    final syncProfile = SyncProfile(
      id: ID(),
      title: state.title,
      scheduleSource: scheduleSource,
      targetCalendar:
          state.targetCalendarChoice == TargetCalendarChoice.createNew
              ? state.newCalendarCreated!
              : state.existingCalendarSelected!,
    );

    final repo = GetIt.I<SyncProfileRepository>();

    try {
      await repo.createSyncProfile(syncProfile);
      emit(state.copyWith(submittedSuccessfully: true));
    } catch (e) {
      emit(state.copyWith(submitError: e.toString()));
    }
  }
}
