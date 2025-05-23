import 'dart:async';
import 'dart:developer';

import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:get_it/get_it.dart';
import 'package:quiver/strings.dart';
import 'package:syncademic_app/models/create_sync_profile_payload.dart';
import 'package:syncademic_app/services/sync_profile_service.dart';
import '../../../services/ics_validation_service.dart';
import 'package:validators/validators.dart';

import '../../../authorization/backend_authorization_service.dart';
import '../../../models/id.dart';
import '../../../models/provider_account.dart';
import '../../../models/schedule_source.dart';
import '../../../models/target_calendar.dart';
import '../../../repositories/target_calendar_repository.dart';
import '../../../services/provider_account_service.dart';
import 'ics_validation_status.dart';

part 'new_sync_profile_cubit.freezed.dart';
part 'new_sync_profile_state.dart';

class NewSyncProfileCubit extends Cubit<NewSyncProfileState> {
  final IcsValidationService icsValidationService;

  NewSyncProfileCubit({IcsValidationService? icsValidationService})
      : icsValidationService =
            icsValidationService ?? GetIt.I<IcsValidationService>(),
        super(const NewSyncProfileState()) {
    GetIt.I<ProviderAccountService>()
        .onCurrentUserChanged
        .listen(providerAccountSelected);
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

    emit(state.copyWith(
      title: title,
      titleError: null,
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

    emit(state.copyWith(
      url: url,
      urlError: null,
      icsValidationStatus: const IcsValidationStatus.notValidated(),
    ));
  }

  Future<void> validateIcs() async {
    assert(isURL(state.url), 'URL must be a valid URL before verifying');

    if (state.icsValidationStatus ==
        const IcsValidationStatus.validationInProgress()) {
      log('Validation already in progress');
      return;
    }

    emit(state.copyWith(
        icsValidationStatus: const IcsValidationStatus.validationInProgress()));

    final result = await icsValidationService.validateUrl(state.url);

    emit(state.copyWith(
      icsValidationStatus: result.fold(
        (error) => IcsValidationStatus.validationFailed(errorMessage: error),
        (result) => result.isValid
            ? IcsValidationStatus.validated(nbEvents: result.nbEvents)
            : IcsValidationStatus.invalid(errorMessage: result.error),
      ),
    ));
  }

  Future<void> providerAccountSelected(
          ProviderAccount? providerAccount) async =>
      emit(
        providerAccount == null
            ? state.copyWith(
                providerAccount: null,
                providerAccountError: 'No provider account selected.',
              )
            : state.copyWith(
                providerAccount: providerAccount,
                providerAccountError: null,
              ),
      );

  Future<void> pickProviderAccount() async {
    await resetProviderAccount();

    try {
      final providerAccount = await GetIt.I<ProviderAccountService>()
          .triggerProviderAccountSelection();
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
    } on ProviderUserIdMismatchException {
      return emit(state.copyWith(
        backendAuthorizationStatus: BackendAuthorizationStatus.notAuthorized,
        backendAuthorizationError:
            'You might have selected the wrong account in the authorization popup. Please try again using your ${state.providerAccount?.providerAccountEmail} account.',
      ));
    } catch (e) {
      return emit(state.copyWith(
        backendAuthorizationStatus: BackendAuthorizationStatus.notAuthorized,
        backendAuthorizationError: e.toString(),
      ));
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

    if (state.currentStep == NewSyncProfileStep.authorizeBackend) {
      unawaited(checkBackendAuthorization());
    }
  }

  void changeNewCalendarColor(GoogleCalendarColor? color) {
    if (color == null) {
      return;
    }
    emit(state.copyWith(targetCalendarColor: color));
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

    final scheduleSource = ScheduleSource(
      url: state.url,
    );

    if (state.providerAccount == null) {
      throw StateError('Provider account must be selected before submitting');
    }

    final targetCalendar =
        state.targetCalendarChoice == TargetCalendarChoice.createNew
            ? TargetCalendarPayload.createNew(
                providerAccountId: state.providerAccount!.providerAccountId,
                colorId: state.targetCalendarColor.id,
              )
            : TargetCalendarPayload.useExisting(
                providerAccountId: state.providerAccount!.providerAccountId,
                calendarId: state.existingCalendarSelected!.id.value,
              );

    final payload = CreateSyncProfileRequest(
      title: state.title,
      scheduleSource: scheduleSource,
      targetCalendar: targetCalendar,
    );

    final syncProfileService = GetIt.I<SyncProfileService>();

    try {
      await syncProfileService.createSyncProfile(payload);
      emit(state.copyWith(submittedSuccessfully: true, isSubmitting: false));
    } catch (e) {
      emit(state.copyWith(submitError: e.toString(), isSubmitting: false));
    }
  }
}
