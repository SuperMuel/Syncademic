import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:get_it/get_it.dart';

import '../../../authorization/backend_authorization_service.dart';
import '../../../models/id.dart';
import '../../../models/sync_profile.dart';
import '../../../repositories/sync_profile_repository.dart';
import '../../../services/sync_profile_service.dart';

part 'sync_profile_cubit.freezed.dart';
part 'sync_profile_state.dart';

class SyncProfileCubit extends Cubit<SyncProfileState> {
  final String syncProfileId;

  SyncProfileCubit(this.syncProfileId)
      : super(const SyncProfileState.loading()) {
    GetIt.I<SyncProfileRepository>()
        .watchSyncProfile(ID.fromString(syncProfileId))
        .listen((syncProfile) {
      emit(syncProfile == null
          ? const SyncProfileState.notFound()
          : state.maybeMap(
              loaded: (loaded) => loaded.copyWith(syncProfile: syncProfile),
              orElse: () => SyncProfileState.loaded(syncProfile),
            ));
    });
  }

  Future<void> requestSync() async {
    final lastSyncRequest = DateTime.now();

    state.maybeMap(
      loaded: (loaded) {
        emit(loaded.copyWith(
          requestSyncError: null,
          lastSyncRequest: lastSyncRequest,
        ));
      },
      orElse: () {},
    );

    try {
      await GetIt.I<SyncProfileService>().requestSync(syncProfileId);

      state.maybeMap(
        loaded: (loaded) => emit(loaded.copyWith(
          requestSyncError: null,
          lastSyncRequest: lastSyncRequest,
        )),
        orElse: () {},
      );
    } catch (e) {
      state.maybeMap(
        loaded: (loaded) => emit(loaded.copyWith(
          requestSyncError: e.toString(),
          lastSyncRequest: null,
        )),
        orElse: () {},
      );
    }
  }

  Future<void> authorizeBackend() =>
      GetIt.I<BackendAuthorizationService>().authorizeBackend();

  Future<void> deleteSyncProfile() async {
    state.maybeMap(
      loaded: (loaded) => emit(loaded.copyWith(isDeleting: true)),
      orElse: () {},
    );

    try {
      await GetIt.I<SyncProfileRepository>()
          .deleteSyncProfile(ID.fromString(syncProfileId));
    } catch (e) {
      state.maybeMap(
        loaded: (loaded) => emit(loaded.copyWith(
          isDeleting: false,
          deletionError: e.toString(),
        )),
        orElse: () {},
      );
      return;
    }

    emit(const SyncProfileState.deleted());
  }
}
