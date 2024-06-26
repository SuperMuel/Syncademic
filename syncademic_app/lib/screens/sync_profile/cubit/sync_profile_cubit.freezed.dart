// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'sync_profile_cubit.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

/// @nodoc
mixin _$SyncProfileState {
  @optionalTypeArgs
  TResult when<TResult extends Object?>({
    required TResult Function() loading,
    required TResult Function(SyncProfile syncProfile, String? requestSyncError,
            DateTime? lastSyncRequest, bool isDeleting, String? deletionError)
        loaded,
    required TResult Function() notFound,
    required TResult Function() deleted,
  }) =>
      throw _privateConstructorUsedError;
  @optionalTypeArgs
  TResult? whenOrNull<TResult extends Object?>({
    TResult? Function()? loading,
    TResult? Function(SyncProfile syncProfile, String? requestSyncError,
            DateTime? lastSyncRequest, bool isDeleting, String? deletionError)?
        loaded,
    TResult? Function()? notFound,
    TResult? Function()? deleted,
  }) =>
      throw _privateConstructorUsedError;
  @optionalTypeArgs
  TResult maybeWhen<TResult extends Object?>({
    TResult Function()? loading,
    TResult Function(SyncProfile syncProfile, String? requestSyncError,
            DateTime? lastSyncRequest, bool isDeleting, String? deletionError)?
        loaded,
    TResult Function()? notFound,
    TResult Function()? deleted,
    required TResult orElse(),
  }) =>
      throw _privateConstructorUsedError;
  @optionalTypeArgs
  TResult map<TResult extends Object?>({
    required TResult Function(_Loading value) loading,
    required TResult Function(_Loaded value) loaded,
    required TResult Function(_NotFound value) notFound,
    required TResult Function(_Deleted value) deleted,
  }) =>
      throw _privateConstructorUsedError;
  @optionalTypeArgs
  TResult? mapOrNull<TResult extends Object?>({
    TResult? Function(_Loading value)? loading,
    TResult? Function(_Loaded value)? loaded,
    TResult? Function(_NotFound value)? notFound,
    TResult? Function(_Deleted value)? deleted,
  }) =>
      throw _privateConstructorUsedError;
  @optionalTypeArgs
  TResult maybeMap<TResult extends Object?>({
    TResult Function(_Loading value)? loading,
    TResult Function(_Loaded value)? loaded,
    TResult Function(_NotFound value)? notFound,
    TResult Function(_Deleted value)? deleted,
    required TResult orElse(),
  }) =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $SyncProfileStateCopyWith<$Res> {
  factory $SyncProfileStateCopyWith(
          SyncProfileState value, $Res Function(SyncProfileState) then) =
      _$SyncProfileStateCopyWithImpl<$Res, SyncProfileState>;
}

/// @nodoc
class _$SyncProfileStateCopyWithImpl<$Res, $Val extends SyncProfileState>
    implements $SyncProfileStateCopyWith<$Res> {
  _$SyncProfileStateCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;
}

/// @nodoc
abstract class _$$LoadingImplCopyWith<$Res> {
  factory _$$LoadingImplCopyWith(
          _$LoadingImpl value, $Res Function(_$LoadingImpl) then) =
      __$$LoadingImplCopyWithImpl<$Res>;
}

/// @nodoc
class __$$LoadingImplCopyWithImpl<$Res>
    extends _$SyncProfileStateCopyWithImpl<$Res, _$LoadingImpl>
    implements _$$LoadingImplCopyWith<$Res> {
  __$$LoadingImplCopyWithImpl(
      _$LoadingImpl _value, $Res Function(_$LoadingImpl) _then)
      : super(_value, _then);
}

/// @nodoc

class _$LoadingImpl extends _Loading {
  const _$LoadingImpl() : super._();

  @override
  String toString() {
    return 'SyncProfileState.loading()';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType && other is _$LoadingImpl);
  }

  @override
  int get hashCode => runtimeType.hashCode;

  @override
  @optionalTypeArgs
  TResult when<TResult extends Object?>({
    required TResult Function() loading,
    required TResult Function(SyncProfile syncProfile, String? requestSyncError,
            DateTime? lastSyncRequest, bool isDeleting, String? deletionError)
        loaded,
    required TResult Function() notFound,
    required TResult Function() deleted,
  }) {
    return loading();
  }

  @override
  @optionalTypeArgs
  TResult? whenOrNull<TResult extends Object?>({
    TResult? Function()? loading,
    TResult? Function(SyncProfile syncProfile, String? requestSyncError,
            DateTime? lastSyncRequest, bool isDeleting, String? deletionError)?
        loaded,
    TResult? Function()? notFound,
    TResult? Function()? deleted,
  }) {
    return loading?.call();
  }

  @override
  @optionalTypeArgs
  TResult maybeWhen<TResult extends Object?>({
    TResult Function()? loading,
    TResult Function(SyncProfile syncProfile, String? requestSyncError,
            DateTime? lastSyncRequest, bool isDeleting, String? deletionError)?
        loaded,
    TResult Function()? notFound,
    TResult Function()? deleted,
    required TResult orElse(),
  }) {
    if (loading != null) {
      return loading();
    }
    return orElse();
  }

  @override
  @optionalTypeArgs
  TResult map<TResult extends Object?>({
    required TResult Function(_Loading value) loading,
    required TResult Function(_Loaded value) loaded,
    required TResult Function(_NotFound value) notFound,
    required TResult Function(_Deleted value) deleted,
  }) {
    return loading(this);
  }

  @override
  @optionalTypeArgs
  TResult? mapOrNull<TResult extends Object?>({
    TResult? Function(_Loading value)? loading,
    TResult? Function(_Loaded value)? loaded,
    TResult? Function(_NotFound value)? notFound,
    TResult? Function(_Deleted value)? deleted,
  }) {
    return loading?.call(this);
  }

  @override
  @optionalTypeArgs
  TResult maybeMap<TResult extends Object?>({
    TResult Function(_Loading value)? loading,
    TResult Function(_Loaded value)? loaded,
    TResult Function(_NotFound value)? notFound,
    TResult Function(_Deleted value)? deleted,
    required TResult orElse(),
  }) {
    if (loading != null) {
      return loading(this);
    }
    return orElse();
  }
}

abstract class _Loading extends SyncProfileState {
  const factory _Loading() = _$LoadingImpl;
  const _Loading._() : super._();
}

/// @nodoc
abstract class _$$LoadedImplCopyWith<$Res> {
  factory _$$LoadedImplCopyWith(
          _$LoadedImpl value, $Res Function(_$LoadedImpl) then) =
      __$$LoadedImplCopyWithImpl<$Res>;
  @useResult
  $Res call(
      {SyncProfile syncProfile,
      String? requestSyncError,
      DateTime? lastSyncRequest,
      bool isDeleting,
      String? deletionError});

  $SyncProfileCopyWith<$Res> get syncProfile;
}

/// @nodoc
class __$$LoadedImplCopyWithImpl<$Res>
    extends _$SyncProfileStateCopyWithImpl<$Res, _$LoadedImpl>
    implements _$$LoadedImplCopyWith<$Res> {
  __$$LoadedImplCopyWithImpl(
      _$LoadedImpl _value, $Res Function(_$LoadedImpl) _then)
      : super(_value, _then);

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? syncProfile = null,
    Object? requestSyncError = freezed,
    Object? lastSyncRequest = freezed,
    Object? isDeleting = null,
    Object? deletionError = freezed,
  }) {
    return _then(_$LoadedImpl(
      null == syncProfile
          ? _value.syncProfile
          : syncProfile // ignore: cast_nullable_to_non_nullable
              as SyncProfile,
      requestSyncError: freezed == requestSyncError
          ? _value.requestSyncError
          : requestSyncError // ignore: cast_nullable_to_non_nullable
              as String?,
      lastSyncRequest: freezed == lastSyncRequest
          ? _value.lastSyncRequest
          : lastSyncRequest // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      isDeleting: null == isDeleting
          ? _value.isDeleting
          : isDeleting // ignore: cast_nullable_to_non_nullable
              as bool,
      deletionError: freezed == deletionError
          ? _value.deletionError
          : deletionError // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }

  @override
  @pragma('vm:prefer-inline')
  $SyncProfileCopyWith<$Res> get syncProfile {
    return $SyncProfileCopyWith<$Res>(_value.syncProfile, (value) {
      return _then(_value.copyWith(syncProfile: value));
    });
  }
}

/// @nodoc

class _$LoadedImpl extends _Loaded {
  const _$LoadedImpl(this.syncProfile,
      {this.requestSyncError,
      this.lastSyncRequest,
      this.isDeleting = false,
      this.deletionError})
      : super._();

  @override
  final SyncProfile syncProfile;
  @override
  final String? requestSyncError;
  @override
  final DateTime? lastSyncRequest;
  @override
  @JsonKey()
  final bool isDeleting;
  @override
  final String? deletionError;

  @override
  String toString() {
    return 'SyncProfileState.loaded(syncProfile: $syncProfile, requestSyncError: $requestSyncError, lastSyncRequest: $lastSyncRequest, isDeleting: $isDeleting, deletionError: $deletionError)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$LoadedImpl &&
            (identical(other.syncProfile, syncProfile) ||
                other.syncProfile == syncProfile) &&
            (identical(other.requestSyncError, requestSyncError) ||
                other.requestSyncError == requestSyncError) &&
            (identical(other.lastSyncRequest, lastSyncRequest) ||
                other.lastSyncRequest == lastSyncRequest) &&
            (identical(other.isDeleting, isDeleting) ||
                other.isDeleting == isDeleting) &&
            (identical(other.deletionError, deletionError) ||
                other.deletionError == deletionError));
  }

  @override
  int get hashCode => Object.hash(runtimeType, syncProfile, requestSyncError,
      lastSyncRequest, isDeleting, deletionError);

  @JsonKey(ignore: true)
  @override
  @pragma('vm:prefer-inline')
  _$$LoadedImplCopyWith<_$LoadedImpl> get copyWith =>
      __$$LoadedImplCopyWithImpl<_$LoadedImpl>(this, _$identity);

  @override
  @optionalTypeArgs
  TResult when<TResult extends Object?>({
    required TResult Function() loading,
    required TResult Function(SyncProfile syncProfile, String? requestSyncError,
            DateTime? lastSyncRequest, bool isDeleting, String? deletionError)
        loaded,
    required TResult Function() notFound,
    required TResult Function() deleted,
  }) {
    return loaded(syncProfile, requestSyncError, lastSyncRequest, isDeleting,
        deletionError);
  }

  @override
  @optionalTypeArgs
  TResult? whenOrNull<TResult extends Object?>({
    TResult? Function()? loading,
    TResult? Function(SyncProfile syncProfile, String? requestSyncError,
            DateTime? lastSyncRequest, bool isDeleting, String? deletionError)?
        loaded,
    TResult? Function()? notFound,
    TResult? Function()? deleted,
  }) {
    return loaded?.call(syncProfile, requestSyncError, lastSyncRequest,
        isDeleting, deletionError);
  }

  @override
  @optionalTypeArgs
  TResult maybeWhen<TResult extends Object?>({
    TResult Function()? loading,
    TResult Function(SyncProfile syncProfile, String? requestSyncError,
            DateTime? lastSyncRequest, bool isDeleting, String? deletionError)?
        loaded,
    TResult Function()? notFound,
    TResult Function()? deleted,
    required TResult orElse(),
  }) {
    if (loaded != null) {
      return loaded(syncProfile, requestSyncError, lastSyncRequest, isDeleting,
          deletionError);
    }
    return orElse();
  }

  @override
  @optionalTypeArgs
  TResult map<TResult extends Object?>({
    required TResult Function(_Loading value) loading,
    required TResult Function(_Loaded value) loaded,
    required TResult Function(_NotFound value) notFound,
    required TResult Function(_Deleted value) deleted,
  }) {
    return loaded(this);
  }

  @override
  @optionalTypeArgs
  TResult? mapOrNull<TResult extends Object?>({
    TResult? Function(_Loading value)? loading,
    TResult? Function(_Loaded value)? loaded,
    TResult? Function(_NotFound value)? notFound,
    TResult? Function(_Deleted value)? deleted,
  }) {
    return loaded?.call(this);
  }

  @override
  @optionalTypeArgs
  TResult maybeMap<TResult extends Object?>({
    TResult Function(_Loading value)? loading,
    TResult Function(_Loaded value)? loaded,
    TResult Function(_NotFound value)? notFound,
    TResult Function(_Deleted value)? deleted,
    required TResult orElse(),
  }) {
    if (loaded != null) {
      return loaded(this);
    }
    return orElse();
  }
}

abstract class _Loaded extends SyncProfileState {
  const factory _Loaded(final SyncProfile syncProfile,
      {final String? requestSyncError,
      final DateTime? lastSyncRequest,
      final bool isDeleting,
      final String? deletionError}) = _$LoadedImpl;
  const _Loaded._() : super._();

  SyncProfile get syncProfile;
  String? get requestSyncError;
  DateTime? get lastSyncRequest;
  bool get isDeleting;
  String? get deletionError;
  @JsonKey(ignore: true)
  _$$LoadedImplCopyWith<_$LoadedImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class _$$NotFoundImplCopyWith<$Res> {
  factory _$$NotFoundImplCopyWith(
          _$NotFoundImpl value, $Res Function(_$NotFoundImpl) then) =
      __$$NotFoundImplCopyWithImpl<$Res>;
}

/// @nodoc
class __$$NotFoundImplCopyWithImpl<$Res>
    extends _$SyncProfileStateCopyWithImpl<$Res, _$NotFoundImpl>
    implements _$$NotFoundImplCopyWith<$Res> {
  __$$NotFoundImplCopyWithImpl(
      _$NotFoundImpl _value, $Res Function(_$NotFoundImpl) _then)
      : super(_value, _then);
}

/// @nodoc

class _$NotFoundImpl extends _NotFound {
  const _$NotFoundImpl() : super._();

  @override
  String toString() {
    return 'SyncProfileState.notFound()';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType && other is _$NotFoundImpl);
  }

  @override
  int get hashCode => runtimeType.hashCode;

  @override
  @optionalTypeArgs
  TResult when<TResult extends Object?>({
    required TResult Function() loading,
    required TResult Function(SyncProfile syncProfile, String? requestSyncError,
            DateTime? lastSyncRequest, bool isDeleting, String? deletionError)
        loaded,
    required TResult Function() notFound,
    required TResult Function() deleted,
  }) {
    return notFound();
  }

  @override
  @optionalTypeArgs
  TResult? whenOrNull<TResult extends Object?>({
    TResult? Function()? loading,
    TResult? Function(SyncProfile syncProfile, String? requestSyncError,
            DateTime? lastSyncRequest, bool isDeleting, String? deletionError)?
        loaded,
    TResult? Function()? notFound,
    TResult? Function()? deleted,
  }) {
    return notFound?.call();
  }

  @override
  @optionalTypeArgs
  TResult maybeWhen<TResult extends Object?>({
    TResult Function()? loading,
    TResult Function(SyncProfile syncProfile, String? requestSyncError,
            DateTime? lastSyncRequest, bool isDeleting, String? deletionError)?
        loaded,
    TResult Function()? notFound,
    TResult Function()? deleted,
    required TResult orElse(),
  }) {
    if (notFound != null) {
      return notFound();
    }
    return orElse();
  }

  @override
  @optionalTypeArgs
  TResult map<TResult extends Object?>({
    required TResult Function(_Loading value) loading,
    required TResult Function(_Loaded value) loaded,
    required TResult Function(_NotFound value) notFound,
    required TResult Function(_Deleted value) deleted,
  }) {
    return notFound(this);
  }

  @override
  @optionalTypeArgs
  TResult? mapOrNull<TResult extends Object?>({
    TResult? Function(_Loading value)? loading,
    TResult? Function(_Loaded value)? loaded,
    TResult? Function(_NotFound value)? notFound,
    TResult? Function(_Deleted value)? deleted,
  }) {
    return notFound?.call(this);
  }

  @override
  @optionalTypeArgs
  TResult maybeMap<TResult extends Object?>({
    TResult Function(_Loading value)? loading,
    TResult Function(_Loaded value)? loaded,
    TResult Function(_NotFound value)? notFound,
    TResult Function(_Deleted value)? deleted,
    required TResult orElse(),
  }) {
    if (notFound != null) {
      return notFound(this);
    }
    return orElse();
  }
}

abstract class _NotFound extends SyncProfileState {
  const factory _NotFound() = _$NotFoundImpl;
  const _NotFound._() : super._();
}

/// @nodoc
abstract class _$$DeletedImplCopyWith<$Res> {
  factory _$$DeletedImplCopyWith(
          _$DeletedImpl value, $Res Function(_$DeletedImpl) then) =
      __$$DeletedImplCopyWithImpl<$Res>;
}

/// @nodoc
class __$$DeletedImplCopyWithImpl<$Res>
    extends _$SyncProfileStateCopyWithImpl<$Res, _$DeletedImpl>
    implements _$$DeletedImplCopyWith<$Res> {
  __$$DeletedImplCopyWithImpl(
      _$DeletedImpl _value, $Res Function(_$DeletedImpl) _then)
      : super(_value, _then);
}

/// @nodoc

class _$DeletedImpl extends _Deleted {
  const _$DeletedImpl() : super._();

  @override
  String toString() {
    return 'SyncProfileState.deleted()';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType && other is _$DeletedImpl);
  }

  @override
  int get hashCode => runtimeType.hashCode;

  @override
  @optionalTypeArgs
  TResult when<TResult extends Object?>({
    required TResult Function() loading,
    required TResult Function(SyncProfile syncProfile, String? requestSyncError,
            DateTime? lastSyncRequest, bool isDeleting, String? deletionError)
        loaded,
    required TResult Function() notFound,
    required TResult Function() deleted,
  }) {
    return deleted();
  }

  @override
  @optionalTypeArgs
  TResult? whenOrNull<TResult extends Object?>({
    TResult? Function()? loading,
    TResult? Function(SyncProfile syncProfile, String? requestSyncError,
            DateTime? lastSyncRequest, bool isDeleting, String? deletionError)?
        loaded,
    TResult? Function()? notFound,
    TResult? Function()? deleted,
  }) {
    return deleted?.call();
  }

  @override
  @optionalTypeArgs
  TResult maybeWhen<TResult extends Object?>({
    TResult Function()? loading,
    TResult Function(SyncProfile syncProfile, String? requestSyncError,
            DateTime? lastSyncRequest, bool isDeleting, String? deletionError)?
        loaded,
    TResult Function()? notFound,
    TResult Function()? deleted,
    required TResult orElse(),
  }) {
    if (deleted != null) {
      return deleted();
    }
    return orElse();
  }

  @override
  @optionalTypeArgs
  TResult map<TResult extends Object?>({
    required TResult Function(_Loading value) loading,
    required TResult Function(_Loaded value) loaded,
    required TResult Function(_NotFound value) notFound,
    required TResult Function(_Deleted value) deleted,
  }) {
    return deleted(this);
  }

  @override
  @optionalTypeArgs
  TResult? mapOrNull<TResult extends Object?>({
    TResult? Function(_Loading value)? loading,
    TResult? Function(_Loaded value)? loaded,
    TResult? Function(_NotFound value)? notFound,
    TResult? Function(_Deleted value)? deleted,
  }) {
    return deleted?.call(this);
  }

  @override
  @optionalTypeArgs
  TResult maybeMap<TResult extends Object?>({
    TResult Function(_Loading value)? loading,
    TResult Function(_Loaded value)? loaded,
    TResult Function(_NotFound value)? notFound,
    TResult Function(_Deleted value)? deleted,
    required TResult orElse(),
  }) {
    if (deleted != null) {
      return deleted(this);
    }
    return orElse();
  }
}

abstract class _Deleted extends SyncProfileState {
  const factory _Deleted() = _$DeletedImpl;
  const _Deleted._() : super._();
}
