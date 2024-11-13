import 'dart:async';
import 'dart:developer';

import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:get_it/get_it.dart';
import 'package:quiver/strings.dart';
import 'package:validators/validators.dart';

import '../../../authorization/backend_authorization_service.dart';
import '../../../models/id.dart';
import '../../../models/provider_account.dart';
import '../../../models/schedule_source.dart';
import '../../../models/sync_profile.dart';
import '../../../models/sync_profile_status.dart';
import '../../../models/target_calendar.dart';
import '../../../repositories/sync_profile_repository.dart';
import '../../../repositories/target_calendar_repository.dart';
import '../../../services/ics_verifier.dart';
import '../../../services/provider_account_service.dart';
import 'ics_verification_status.dart';

part 'new_sync_profile_cubit.freezed.dart';
part 'new_sync_profile_state.dart';

class NewSyncProfileCubit extends Cubit<NewSyncProfileState> {
  final IcsValidationService icsService;

  NewSyncProfileCubit({this.icsService = const IcsValidationService()})
      : super(const NewSyncProfileState()) {
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

    emit(state.copyWith(
      url: url,
      urlError: null,
      icsVerificationStatus: const IcsVerificationStatus.notVerified(),
    ));
  }

  Future<void> verifyIcs() async {
    assert(isURL(state.url), 'URL must be a valid URL before verifying');

    if (state.icsVerificationStatus ==
        const IcsVerificationStatus.verificationInProgress()) {
      return;
    }

    emit(state.copyWith(
        icsVerificationStatus:
            const IcsVerificationStatus.verificationInProgress()));

    final verificationResult = await icsService.fetchAndParseIcs(state.url);

    verificationResult.fold(
        (error) => emit(state.copyWith(
            icsVerificationStatus:
                IcsVerificationStatus.verificationFailed(errorMessage: error))),
        (_) => emit(state.copyWith(
            icsVerificationStatus: const IcsVerificationStatus.verified())));
  }

  Future<void> providerAccountSelected(ProviderAccount? providerAccount) async {
    if (providerAccount == null) {
      return emit(state.copyWith(
        providerAccount: null,
        providerAccountError: 'No provider account selected.',
      ));
    }

    emit(state.copyWith(
      providerAccount: providerAccount,
      providerAccountError: null,
    ));
  }

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
      //TODO : handle UserIdMismatchException
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

    late TargetCalendar targetCalendar;
    if (state.targetCalendarChoice == TargetCalendarChoice.createNew) {
      try {
        targetCalendar =
            await GetIt.I<TargetCalendarRepository>().createCalendar(
          state.providerAccount!.providerAccountId,
          state.newCalendarCreated!,
          color: state.targetCalendarColor,
        ); //TODO : move the creation responsability to the backend
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
      status: const SyncProfileStatus.notStarted(),
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
