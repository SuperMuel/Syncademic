import 'dart:async';
import 'dart:developer';

import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:get_it/get_it.dart';
import 'package:quiver/strings.dart';
import 'package:syncademic_app/models/provider_account.dart';
import 'package:syncademic_app/services/provider_account_service.dart';
import '../../../repositories/target_calendar_repository.dart';
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
        id: ID(), // Will be overwritten by the calendar API
        title: title,
        providerAccountId: '',
        createdBySyncademic: true,
        description: "Calendar created by Syncademic.io",
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

  void providerAccountSelected(ProviderAccount providerAccount) =>
      emit(state.copyWith(
        providerAccount: providerAccount,
        providerAccountError: null,
      ));

  Future<void> pickProviderAccount() async {
    await resetProviderAccount();

    try {
      final providerAccount = await GetIt.I<ProviderAccountService>()
          .triggerProviderAccountSelection();
      if (providerAccount == null) {
        return emit(state.copyWith(
          providerAccount: null,
          providerAccountError: 'No provider account selected.',
        ));
      }

      providerAccountSelected(providerAccount);
    } catch (e) {
      return emit(state.copyWith(
        providerAccount: null,
        providerAccountError: "Error selecting provider account: $e",
      ));
    }
  }

  Future<void> resetProviderAccount() async {
    await GetIt.I<ProviderAccountService>().reset();
    emit(state.copyWith(providerAccount: null, providerAccountError: null));
  }

  void targetCalendarChoiceChanged(Set<TargetCalendarChoice> choice) {
    if (choice.length != 1) {
      throw ArgumentError('Exactly one choice must be selected');
    }
    emit(state.copyWith(targetCalendarChoice: choice.first));
  }

  void selectExistingCalendar(TargetCalendar? calendar) {
    if (calendar == null) {
      return;
    }
    emit(state.copyWith(existingCalendarSelected: calendar));
  }

  void authorizeBackend() async {
    if (state.providerAccount == null) {
      throw StateError('Provider account must be selected before authorizing');
    }

    emit(state.copyWith(
      backendAuthorizationStatus: BackendAuthorizationStatus.authorizing,
      backendAuthorizationError: null,
    ));

    try {
      await GetIt.I<BackendAuthorizationService>()
          .authorizeBackend(state.providerAccount!);
      //TODO : handle UserIdMismatchException
    } catch (e) {
      emit(state.copyWith(
        backendAuthorizationStatus: BackendAuthorizationStatus.notAuthorized,
        backendAuthorizationError: e.toString(),
      ));
      return;
    }

    emit(state.copyWith(
      backendAuthorizationStatus: BackendAuthorizationStatus.authorized,
      backendAuthorizationError: null,
    ));
  }

  void next() {
    if (state.canContinue) {
      emit(state.copyWith(currentStep: state.currentStep.next));
    }

    if (state.currentStep == NewSyncProfileStep.authorizeBackend) {
      unawaited(checkBackendAuthorization());
    }
  }

  Future<void> checkBackendAuthorization() async {
    log("Checking backend authorization");
    final providerAccount = state.providerAccount;

    if (providerAccount == null) {
      throw StateError('Provider account must be selected before authorizing');
    }

    emit(state.copyWith(
      backendAuthorizationStatus: BackendAuthorizationStatus.checking,
      backendAuthorizationError: null,
    ));

    try {
      final isAuthorized = await GetIt.I<BackendAuthorizationService>()
          .isAuthorized(providerAccount);

      log("Backend is authorized: $isAuthorized");

      return emit(state.copyWith(
        backendAuthorizationStatus: isAuthorized
            ? BackendAuthorizationStatus.authorized
            : BackendAuthorizationStatus.notAuthorized,
        backendAuthorizationError: null,
      ));
    } catch (e) {
      emit(state.copyWith(
        backendAuthorizationStatus: BackendAuthorizationStatus.notAuthorized,
        backendAuthorizationError: e.toString(),
      ));
    }
  }

  void previous() {
    if (state.canGoBack) {
      emit(state.copyWith(currentStep: state.currentStep.previous));
    }
  }

  Future<void> submit() async {
    if (!state.canSubmit()) {
      return emit(state.copyWith(
        submitError:
            'Cannot submit invalid form. Please check each step again. If the issue persists, please contact support.',
        isSubmitting: false,
      ));
    }

    emit(state.copyWith(isSubmitting: true));

    late TargetCalendar targetCalendar;
    if (state.targetCalendarChoice == TargetCalendarChoice.createNew) {
      try {
        targetCalendar = await GetIt.I<TargetCalendarRepository>().createCalendar(
            state.providerAccount!.providerAccountId,
            state
                .newCalendarCreated!); //TODO : move the creation responsability to the backend
      } catch (e) {
        return emit(
            state.copyWith(submitError: e.toString(), isSubmitting: false));
      }
    } else {
      targetCalendar = state.existingCalendarSelected!;
    }

    final scheduleSource = ScheduleSource(
      url: state.url,
    );

    final syncProfile = SyncProfile(
      id: ID(),
      title: state.title,
      scheduleSource: scheduleSource,
      targetCalendar: targetCalendar,
    );

    final repo = GetIt.I<SyncProfileRepository>();

    try {
      await repo.createSyncProfile(syncProfile);
      emit(state.copyWith(submittedSuccessfully: true, isSubmitting: false));
    } catch (e) {
      emit(state.copyWith(submitError: e.toString(), isSubmitting: false));
    }
  }
}
