import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:get_it/get_it.dart';
import '../../../authorization/backend_authorization_service.dart';
import '../../../models/id.dart';
import '../../../models/sync_profile.dart';
import '../../../services/sync_profile_service.dart';

import '../../../repositories/sync_profile_repository.dart';

part 'sync_profile_state.dart';
part 'sync_profile_cubit.freezed.dart';

class SyncProfileCubit extends Cubit<SyncProfileState> {
  final String syncProfileId;

  SyncProfileCubit(this.syncProfileId)
      : super(const SyncProfileState.loading()) {
    GetIt.I<SyncProfileRepository>()
        .watchSyncProfile(ID.fromString(syncProfileId))
        .listen((syncProfile) => emit(syncProfile == null
            ? const SyncProfileState.notFound()
            : SyncProfileState.loaded(syncProfile)));
  }

  Future<void> requestSync() =>
      GetIt.I<SyncProfileService>().requestSync(syncProfileId);

  Future<void> authorizeBackend() =>
      GetIt.I<BackendAuthorizationService>().authorizeBackend(syncProfileId);
}
