part of 'sync_profile_cubit.dart';

@freezed
class SyncProfileState with _$SyncProfileState {
  const factory SyncProfileState.loading() = _Loading;
  const factory SyncProfileState.loaded(SyncProfile syncProfile) = _Loaded;
  const factory SyncProfileState.notFound() = _NotFound;
}
