import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:get_it/get_it.dart';
import 'package:syncademic_app/models/id.dart';
import 'package:syncademic_app/models/sync_profile.dart';
import 'package:syncademic_app/services/sync_profile_service.dart';

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
}
