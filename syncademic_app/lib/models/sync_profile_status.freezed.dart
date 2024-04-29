// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'sync_profile_status.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

/// @nodoc
mixin _$SyncProfileStatus {
  DateTime? get lastSuccessfulSync => throw _privateConstructorUsedError;
  @optionalTypeArgs
  TResult when<TResult extends Object?>({
    required TResult Function(String? syncTrigger, DateTime? lastSuccessfulSync)
        success,
    required TResult Function(String? syncTrigger, DateTime? lastSuccessfulSync)
        inProgress,
    required TResult Function(
            String message, String? syncTrigger, DateTime? lastSuccessfulSync)
        failed,
    required TResult Function(String? syncTrigger, DateTime? lastSuccessfulSync)
        notStarted,
    required TResult Function(DateTime? lastSuccessfulSync) deleting,
    required TResult Function(String message, DateTime? lastSuccessfulSync)
        deletionFailed,
  }) =>
      throw _privateConstructorUsedError;
  @optionalTypeArgs
  TResult? whenOrNull<TResult extends Object?>({
    TResult? Function(String? syncTrigger, DateTime? lastSuccessfulSync)?
        success,
    TResult? Function(String? syncTrigger, DateTime? lastSuccessfulSync)?
        inProgress,
    TResult? Function(
            String message, String? syncTrigger, DateTime? lastSuccessfulSync)?
        failed,
    TResult? Function(String? syncTrigger, DateTime? lastSuccessfulSync)?
        notStarted,
    TResult? Function(DateTime? lastSuccessfulSync)? deleting,
    TResult? Function(String message, DateTime? lastSuccessfulSync)?
        deletionFailed,
  }) =>
      throw _privateConstructorUsedError;
  @optionalTypeArgs
  TResult maybeWhen<TResult extends Object?>({
    TResult Function(String? syncTrigger, DateTime? lastSuccessfulSync)?
        success,
    TResult Function(String? syncTrigger, DateTime? lastSuccessfulSync)?
        inProgress,
    TResult Function(
            String message, String? syncTrigger, DateTime? lastSuccessfulSync)?
        failed,
    TResult Function(String? syncTrigger, DateTime? lastSuccessfulSync)?
        notStarted,
    TResult Function(DateTime? lastSuccessfulSync)? deleting,
    TResult Function(String message, DateTime? lastSuccessfulSync)?
        deletionFailed,
    required TResult orElse(),
  }) =>
      throw _privateConstructorUsedError;
  @optionalTypeArgs
  TResult map<TResult extends Object?>({
    required TResult Function(_Success value) success,
    required TResult Function(_InProgress value) inProgress,
    required TResult Function(_Failed value) failed,
    required TResult Function(_NotStarted value) notStarted,
    required TResult Function(_Deleting value) deleting,
    required TResult Function(_DeletionFailed value) deletionFailed,
  }) =>
      throw _privateConstructorUsedError;
  @optionalTypeArgs
  TResult? mapOrNull<TResult extends Object?>({
    TResult? Function(_Success value)? success,
    TResult? Function(_InProgress value)? inProgress,
    TResult? Function(_Failed value)? failed,
    TResult? Function(_NotStarted value)? notStarted,
    TResult? Function(_Deleting value)? deleting,
    TResult? Function(_DeletionFailed value)? deletionFailed,
  }) =>
      throw _privateConstructorUsedError;
  @optionalTypeArgs
  TResult maybeMap<TResult extends Object?>({
    TResult Function(_Success value)? success,
    TResult Function(_InProgress value)? inProgress,
    TResult Function(_Failed value)? failed,
    TResult Function(_NotStarted value)? notStarted,
    TResult Function(_Deleting value)? deleting,
    TResult Function(_DeletionFailed value)? deletionFailed,
    required TResult orElse(),
  }) =>
      throw _privateConstructorUsedError;

  @JsonKey(ignore: true)
  $SyncProfileStatusCopyWith<SyncProfileStatus> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $SyncProfileStatusCopyWith<$Res> {
  factory $SyncProfileStatusCopyWith(
          SyncProfileStatus value, $Res Function(SyncProfileStatus) then) =
      _$SyncProfileStatusCopyWithImpl<$Res, SyncProfileStatus>;
  @useResult
  $Res call({DateTime? lastSuccessfulSync});
}

/// @nodoc
class _$SyncProfileStatusCopyWithImpl<$Res, $Val extends SyncProfileStatus>
    implements $SyncProfileStatusCopyWith<$Res> {
  _$SyncProfileStatusCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? lastSuccessfulSync = freezed,
  }) {
    return _then(_value.copyWith(
      lastSuccessfulSync: freezed == lastSuccessfulSync
          ? _value.lastSuccessfulSync
          : lastSuccessfulSync // ignore: cast_nullable_to_non_nullable
              as DateTime?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$SuccessImplCopyWith<$Res>
    implements $SyncProfileStatusCopyWith<$Res> {
  factory _$$SuccessImplCopyWith(
          _$SuccessImpl value, $Res Function(_$SuccessImpl) then) =
      __$$SuccessImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({String? syncTrigger, DateTime? lastSuccessfulSync});
}

/// @nodoc
class __$$SuccessImplCopyWithImpl<$Res>
    extends _$SyncProfileStatusCopyWithImpl<$Res, _$SuccessImpl>
    implements _$$SuccessImplCopyWith<$Res> {
  __$$SuccessImplCopyWithImpl(
      _$SuccessImpl _value, $Res Function(_$SuccessImpl) _then)
      : super(_value, _then);

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? syncTrigger = freezed,
    Object? lastSuccessfulSync = freezed,
  }) {
    return _then(_$SuccessImpl(
      syncTrigger: freezed == syncTrigger
          ? _value.syncTrigger
          : syncTrigger // ignore: cast_nullable_to_non_nullable
              as String?,
      lastSuccessfulSync: freezed == lastSuccessfulSync
          ? _value.lastSuccessfulSync
          : lastSuccessfulSync // ignore: cast_nullable_to_non_nullable
              as DateTime?,
    ));
  }
}

/// @nodoc

class _$SuccessImpl extends _Success {
  const _$SuccessImpl({this.syncTrigger, this.lastSuccessfulSync}) : super._();

  @override
  final String? syncTrigger;
  @override
  final DateTime? lastSuccessfulSync;

  @override
  String toString() {
    return 'SyncProfileStatus.success(syncTrigger: $syncTrigger, lastSuccessfulSync: $lastSuccessfulSync)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$SuccessImpl &&
            (identical(other.syncTrigger, syncTrigger) ||
                other.syncTrigger == syncTrigger) &&
            (identical(other.lastSuccessfulSync, lastSuccessfulSync) ||
                other.lastSuccessfulSync == lastSuccessfulSync));
  }

  @override
  int get hashCode => Object.hash(runtimeType, syncTrigger, lastSuccessfulSync);

  @JsonKey(ignore: true)
  @override
  @pragma('vm:prefer-inline')
  _$$SuccessImplCopyWith<_$SuccessImpl> get copyWith =>
      __$$SuccessImplCopyWithImpl<_$SuccessImpl>(this, _$identity);

  @override
  @optionalTypeArgs
  TResult when<TResult extends Object?>({
    required TResult Function(String? syncTrigger, DateTime? lastSuccessfulSync)
        success,
    required TResult Function(String? syncTrigger, DateTime? lastSuccessfulSync)
        inProgress,
    required TResult Function(
            String message, String? syncTrigger, DateTime? lastSuccessfulSync)
        failed,
    required TResult Function(String? syncTrigger, DateTime? lastSuccessfulSync)
        notStarted,
    required TResult Function(DateTime? lastSuccessfulSync) deleting,
    required TResult Function(String message, DateTime? lastSuccessfulSync)
        deletionFailed,
  }) {
    return success(syncTrigger, lastSuccessfulSync);
  }

  @override
  @optionalTypeArgs
  TResult? whenOrNull<TResult extends Object?>({
    TResult? Function(String? syncTrigger, DateTime? lastSuccessfulSync)?
        success,
    TResult? Function(String? syncTrigger, DateTime? lastSuccessfulSync)?
        inProgress,
    TResult? Function(
            String message, String? syncTrigger, DateTime? lastSuccessfulSync)?
        failed,
    TResult? Function(String? syncTrigger, DateTime? lastSuccessfulSync)?
        notStarted,
    TResult? Function(DateTime? lastSuccessfulSync)? deleting,
    TResult? Function(String message, DateTime? lastSuccessfulSync)?
        deletionFailed,
  }) {
    return success?.call(syncTrigger, lastSuccessfulSync);
  }

  @override
  @optionalTypeArgs
  TResult maybeWhen<TResult extends Object?>({
    TResult Function(String? syncTrigger, DateTime? lastSuccessfulSync)?
        success,
    TResult Function(String? syncTrigger, DateTime? lastSuccessfulSync)?
        inProgress,
    TResult Function(
            String message, String? syncTrigger, DateTime? lastSuccessfulSync)?
        failed,
    TResult Function(String? syncTrigger, DateTime? lastSuccessfulSync)?
        notStarted,
    TResult Function(DateTime? lastSuccessfulSync)? deleting,
    TResult Function(String message, DateTime? lastSuccessfulSync)?
        deletionFailed,
    required TResult orElse(),
  }) {
    if (success != null) {
      return success(syncTrigger, lastSuccessfulSync);
    }
    return orElse();
  }

  @override
  @optionalTypeArgs
  TResult map<TResult extends Object?>({
    required TResult Function(_Success value) success,
    required TResult Function(_InProgress value) inProgress,
    required TResult Function(_Failed value) failed,
    required TResult Function(_NotStarted value) notStarted,
    required TResult Function(_Deleting value) deleting,
    required TResult Function(_DeletionFailed value) deletionFailed,
  }) {
    return success(this);
  }

  @override
  @optionalTypeArgs
  TResult? mapOrNull<TResult extends Object?>({
    TResult? Function(_Success value)? success,
    TResult? Function(_InProgress value)? inProgress,
    TResult? Function(_Failed value)? failed,
    TResult? Function(_NotStarted value)? notStarted,
    TResult? Function(_Deleting value)? deleting,
    TResult? Function(_DeletionFailed value)? deletionFailed,
  }) {
    return success?.call(this);
  }

  @override
  @optionalTypeArgs
  TResult maybeMap<TResult extends Object?>({
    TResult Function(_Success value)? success,
    TResult Function(_InProgress value)? inProgress,
    TResult Function(_Failed value)? failed,
    TResult Function(_NotStarted value)? notStarted,
    TResult Function(_Deleting value)? deleting,
    TResult Function(_DeletionFailed value)? deletionFailed,
    required TResult orElse(),
  }) {
    if (success != null) {
      return success(this);
    }
    return orElse();
  }
}

abstract class _Success extends SyncProfileStatus {
  const factory _Success(
      {final String? syncTrigger,
      final DateTime? lastSuccessfulSync}) = _$SuccessImpl;
  const _Success._() : super._();

  String? get syncTrigger;
  @override
  DateTime? get lastSuccessfulSync;
  @override
  @JsonKey(ignore: true)
  _$$SuccessImplCopyWith<_$SuccessImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class _$$InProgressImplCopyWith<$Res>
    implements $SyncProfileStatusCopyWith<$Res> {
  factory _$$InProgressImplCopyWith(
          _$InProgressImpl value, $Res Function(_$InProgressImpl) then) =
      __$$InProgressImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({String? syncTrigger, DateTime? lastSuccessfulSync});
}

/// @nodoc
class __$$InProgressImplCopyWithImpl<$Res>
    extends _$SyncProfileStatusCopyWithImpl<$Res, _$InProgressImpl>
    implements _$$InProgressImplCopyWith<$Res> {
  __$$InProgressImplCopyWithImpl(
      _$InProgressImpl _value, $Res Function(_$InProgressImpl) _then)
      : super(_value, _then);

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? syncTrigger = freezed,
    Object? lastSuccessfulSync = freezed,
  }) {
    return _then(_$InProgressImpl(
      syncTrigger: freezed == syncTrigger
          ? _value.syncTrigger
          : syncTrigger // ignore: cast_nullable_to_non_nullable
              as String?,
      lastSuccessfulSync: freezed == lastSuccessfulSync
          ? _value.lastSuccessfulSync
          : lastSuccessfulSync // ignore: cast_nullable_to_non_nullable
              as DateTime?,
    ));
  }
}

/// @nodoc

class _$InProgressImpl extends _InProgress {
  const _$InProgressImpl({this.syncTrigger, this.lastSuccessfulSync})
      : super._();

  @override
  final String? syncTrigger;
  @override
  final DateTime? lastSuccessfulSync;

  @override
  String toString() {
    return 'SyncProfileStatus.inProgress(syncTrigger: $syncTrigger, lastSuccessfulSync: $lastSuccessfulSync)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$InProgressImpl &&
            (identical(other.syncTrigger, syncTrigger) ||
                other.syncTrigger == syncTrigger) &&
            (identical(other.lastSuccessfulSync, lastSuccessfulSync) ||
                other.lastSuccessfulSync == lastSuccessfulSync));
  }

  @override
  int get hashCode => Object.hash(runtimeType, syncTrigger, lastSuccessfulSync);

  @JsonKey(ignore: true)
  @override
  @pragma('vm:prefer-inline')
  _$$InProgressImplCopyWith<_$InProgressImpl> get copyWith =>
      __$$InProgressImplCopyWithImpl<_$InProgressImpl>(this, _$identity);

  @override
  @optionalTypeArgs
  TResult when<TResult extends Object?>({
    required TResult Function(String? syncTrigger, DateTime? lastSuccessfulSync)
        success,
    required TResult Function(String? syncTrigger, DateTime? lastSuccessfulSync)
        inProgress,
    required TResult Function(
            String message, String? syncTrigger, DateTime? lastSuccessfulSync)
        failed,
    required TResult Function(String? syncTrigger, DateTime? lastSuccessfulSync)
        notStarted,
    required TResult Function(DateTime? lastSuccessfulSync) deleting,
    required TResult Function(String message, DateTime? lastSuccessfulSync)
        deletionFailed,
  }) {
    return inProgress(syncTrigger, lastSuccessfulSync);
  }

  @override
  @optionalTypeArgs
  TResult? whenOrNull<TResult extends Object?>({
    TResult? Function(String? syncTrigger, DateTime? lastSuccessfulSync)?
        success,
    TResult? Function(String? syncTrigger, DateTime? lastSuccessfulSync)?
        inProgress,
    TResult? Function(
            String message, String? syncTrigger, DateTime? lastSuccessfulSync)?
        failed,
    TResult? Function(String? syncTrigger, DateTime? lastSuccessfulSync)?
        notStarted,
    TResult? Function(DateTime? lastSuccessfulSync)? deleting,
    TResult? Function(String message, DateTime? lastSuccessfulSync)?
        deletionFailed,
  }) {
    return inProgress?.call(syncTrigger, lastSuccessfulSync);
  }

  @override
  @optionalTypeArgs
  TResult maybeWhen<TResult extends Object?>({
    TResult Function(String? syncTrigger, DateTime? lastSuccessfulSync)?
        success,
    TResult Function(String? syncTrigger, DateTime? lastSuccessfulSync)?
        inProgress,
    TResult Function(
            String message, String? syncTrigger, DateTime? lastSuccessfulSync)?
        failed,
    TResult Function(String? syncTrigger, DateTime? lastSuccessfulSync)?
        notStarted,
    TResult Function(DateTime? lastSuccessfulSync)? deleting,
    TResult Function(String message, DateTime? lastSuccessfulSync)?
        deletionFailed,
    required TResult orElse(),
  }) {
    if (inProgress != null) {
      return inProgress(syncTrigger, lastSuccessfulSync);
    }
    return orElse();
  }

  @override
  @optionalTypeArgs
  TResult map<TResult extends Object?>({
    required TResult Function(_Success value) success,
    required TResult Function(_InProgress value) inProgress,
    required TResult Function(_Failed value) failed,
    required TResult Function(_NotStarted value) notStarted,
    required TResult Function(_Deleting value) deleting,
    required TResult Function(_DeletionFailed value) deletionFailed,
  }) {
    return inProgress(this);
  }

  @override
  @optionalTypeArgs
  TResult? mapOrNull<TResult extends Object?>({
    TResult? Function(_Success value)? success,
    TResult? Function(_InProgress value)? inProgress,
    TResult? Function(_Failed value)? failed,
    TResult? Function(_NotStarted value)? notStarted,
    TResult? Function(_Deleting value)? deleting,
    TResult? Function(_DeletionFailed value)? deletionFailed,
  }) {
    return inProgress?.call(this);
  }

  @override
  @optionalTypeArgs
  TResult maybeMap<TResult extends Object?>({
    TResult Function(_Success value)? success,
    TResult Function(_InProgress value)? inProgress,
    TResult Function(_Failed value)? failed,
    TResult Function(_NotStarted value)? notStarted,
    TResult Function(_Deleting value)? deleting,
    TResult Function(_DeletionFailed value)? deletionFailed,
    required TResult orElse(),
  }) {
    if (inProgress != null) {
      return inProgress(this);
    }
    return orElse();
  }
}

abstract class _InProgress extends SyncProfileStatus {
  const factory _InProgress(
      {final String? syncTrigger,
      final DateTime? lastSuccessfulSync}) = _$InProgressImpl;
  const _InProgress._() : super._();

  String? get syncTrigger;
  @override
  DateTime? get lastSuccessfulSync;
  @override
  @JsonKey(ignore: true)
  _$$InProgressImplCopyWith<_$InProgressImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class _$$FailedImplCopyWith<$Res>
    implements $SyncProfileStatusCopyWith<$Res> {
  factory _$$FailedImplCopyWith(
          _$FailedImpl value, $Res Function(_$FailedImpl) then) =
      __$$FailedImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String message, String? syncTrigger, DateTime? lastSuccessfulSync});
}

/// @nodoc
class __$$FailedImplCopyWithImpl<$Res>
    extends _$SyncProfileStatusCopyWithImpl<$Res, _$FailedImpl>
    implements _$$FailedImplCopyWith<$Res> {
  __$$FailedImplCopyWithImpl(
      _$FailedImpl _value, $Res Function(_$FailedImpl) _then)
      : super(_value, _then);

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? message = null,
    Object? syncTrigger = freezed,
    Object? lastSuccessfulSync = freezed,
  }) {
    return _then(_$FailedImpl(
      null == message
          ? _value.message
          : message // ignore: cast_nullable_to_non_nullable
              as String,
      syncTrigger: freezed == syncTrigger
          ? _value.syncTrigger
          : syncTrigger // ignore: cast_nullable_to_non_nullable
              as String?,
      lastSuccessfulSync: freezed == lastSuccessfulSync
          ? _value.lastSuccessfulSync
          : lastSuccessfulSync // ignore: cast_nullable_to_non_nullable
              as DateTime?,
    ));
  }
}

/// @nodoc

class _$FailedImpl extends _Failed {
  const _$FailedImpl(this.message, {this.syncTrigger, this.lastSuccessfulSync})
      : super._();

  @override
  final String message;
  @override
  final String? syncTrigger;
  @override
  final DateTime? lastSuccessfulSync;

  @override
  String toString() {
    return 'SyncProfileStatus.failed(message: $message, syncTrigger: $syncTrigger, lastSuccessfulSync: $lastSuccessfulSync)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$FailedImpl &&
            (identical(other.message, message) || other.message == message) &&
            (identical(other.syncTrigger, syncTrigger) ||
                other.syncTrigger == syncTrigger) &&
            (identical(other.lastSuccessfulSync, lastSuccessfulSync) ||
                other.lastSuccessfulSync == lastSuccessfulSync));
  }

  @override
  int get hashCode =>
      Object.hash(runtimeType, message, syncTrigger, lastSuccessfulSync);

  @JsonKey(ignore: true)
  @override
  @pragma('vm:prefer-inline')
  _$$FailedImplCopyWith<_$FailedImpl> get copyWith =>
      __$$FailedImplCopyWithImpl<_$FailedImpl>(this, _$identity);

  @override
  @optionalTypeArgs
  TResult when<TResult extends Object?>({
    required TResult Function(String? syncTrigger, DateTime? lastSuccessfulSync)
        success,
    required TResult Function(String? syncTrigger, DateTime? lastSuccessfulSync)
        inProgress,
    required TResult Function(
            String message, String? syncTrigger, DateTime? lastSuccessfulSync)
        failed,
    required TResult Function(String? syncTrigger, DateTime? lastSuccessfulSync)
        notStarted,
    required TResult Function(DateTime? lastSuccessfulSync) deleting,
    required TResult Function(String message, DateTime? lastSuccessfulSync)
        deletionFailed,
  }) {
    return failed(message, syncTrigger, lastSuccessfulSync);
  }

  @override
  @optionalTypeArgs
  TResult? whenOrNull<TResult extends Object?>({
    TResult? Function(String? syncTrigger, DateTime? lastSuccessfulSync)?
        success,
    TResult? Function(String? syncTrigger, DateTime? lastSuccessfulSync)?
        inProgress,
    TResult? Function(
            String message, String? syncTrigger, DateTime? lastSuccessfulSync)?
        failed,
    TResult? Function(String? syncTrigger, DateTime? lastSuccessfulSync)?
        notStarted,
    TResult? Function(DateTime? lastSuccessfulSync)? deleting,
    TResult? Function(String message, DateTime? lastSuccessfulSync)?
        deletionFailed,
  }) {
    return failed?.call(message, syncTrigger, lastSuccessfulSync);
  }

  @override
  @optionalTypeArgs
  TResult maybeWhen<TResult extends Object?>({
    TResult Function(String? syncTrigger, DateTime? lastSuccessfulSync)?
        success,
    TResult Function(String? syncTrigger, DateTime? lastSuccessfulSync)?
        inProgress,
    TResult Function(
            String message, String? syncTrigger, DateTime? lastSuccessfulSync)?
        failed,
    TResult Function(String? syncTrigger, DateTime? lastSuccessfulSync)?
        notStarted,
    TResult Function(DateTime? lastSuccessfulSync)? deleting,
    TResult Function(String message, DateTime? lastSuccessfulSync)?
        deletionFailed,
    required TResult orElse(),
  }) {
    if (failed != null) {
      return failed(message, syncTrigger, lastSuccessfulSync);
    }
    return orElse();
  }

  @override
  @optionalTypeArgs
  TResult map<TResult extends Object?>({
    required TResult Function(_Success value) success,
    required TResult Function(_InProgress value) inProgress,
    required TResult Function(_Failed value) failed,
    required TResult Function(_NotStarted value) notStarted,
    required TResult Function(_Deleting value) deleting,
    required TResult Function(_DeletionFailed value) deletionFailed,
  }) {
    return failed(this);
  }

  @override
  @optionalTypeArgs
  TResult? mapOrNull<TResult extends Object?>({
    TResult? Function(_Success value)? success,
    TResult? Function(_InProgress value)? inProgress,
    TResult? Function(_Failed value)? failed,
    TResult? Function(_NotStarted value)? notStarted,
    TResult? Function(_Deleting value)? deleting,
    TResult? Function(_DeletionFailed value)? deletionFailed,
  }) {
    return failed?.call(this);
  }

  @override
  @optionalTypeArgs
  TResult maybeMap<TResult extends Object?>({
    TResult Function(_Success value)? success,
    TResult Function(_InProgress value)? inProgress,
    TResult Function(_Failed value)? failed,
    TResult Function(_NotStarted value)? notStarted,
    TResult Function(_Deleting value)? deleting,
    TResult Function(_DeletionFailed value)? deletionFailed,
    required TResult orElse(),
  }) {
    if (failed != null) {
      return failed(this);
    }
    return orElse();
  }
}

abstract class _Failed extends SyncProfileStatus {
  const factory _Failed(final String message,
      {final String? syncTrigger,
      final DateTime? lastSuccessfulSync}) = _$FailedImpl;
  const _Failed._() : super._();

  String get message;
  String? get syncTrigger;
  @override
  DateTime? get lastSuccessfulSync;
  @override
  @JsonKey(ignore: true)
  _$$FailedImplCopyWith<_$FailedImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class _$$NotStartedImplCopyWith<$Res>
    implements $SyncProfileStatusCopyWith<$Res> {
  factory _$$NotStartedImplCopyWith(
          _$NotStartedImpl value, $Res Function(_$NotStartedImpl) then) =
      __$$NotStartedImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({String? syncTrigger, DateTime? lastSuccessfulSync});
}

/// @nodoc
class __$$NotStartedImplCopyWithImpl<$Res>
    extends _$SyncProfileStatusCopyWithImpl<$Res, _$NotStartedImpl>
    implements _$$NotStartedImplCopyWith<$Res> {
  __$$NotStartedImplCopyWithImpl(
      _$NotStartedImpl _value, $Res Function(_$NotStartedImpl) _then)
      : super(_value, _then);

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? syncTrigger = freezed,
    Object? lastSuccessfulSync = freezed,
  }) {
    return _then(_$NotStartedImpl(
      syncTrigger: freezed == syncTrigger
          ? _value.syncTrigger
          : syncTrigger // ignore: cast_nullable_to_non_nullable
              as String?,
      lastSuccessfulSync: freezed == lastSuccessfulSync
          ? _value.lastSuccessfulSync
          : lastSuccessfulSync // ignore: cast_nullable_to_non_nullable
              as DateTime?,
    ));
  }
}

/// @nodoc

class _$NotStartedImpl extends _NotStarted {
  const _$NotStartedImpl({this.syncTrigger, this.lastSuccessfulSync})
      : super._();

  @override
  final String? syncTrigger;
  @override
  final DateTime? lastSuccessfulSync;

  @override
  String toString() {
    return 'SyncProfileStatus.notStarted(syncTrigger: $syncTrigger, lastSuccessfulSync: $lastSuccessfulSync)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$NotStartedImpl &&
            (identical(other.syncTrigger, syncTrigger) ||
                other.syncTrigger == syncTrigger) &&
            (identical(other.lastSuccessfulSync, lastSuccessfulSync) ||
                other.lastSuccessfulSync == lastSuccessfulSync));
  }

  @override
  int get hashCode => Object.hash(runtimeType, syncTrigger, lastSuccessfulSync);

  @JsonKey(ignore: true)
  @override
  @pragma('vm:prefer-inline')
  _$$NotStartedImplCopyWith<_$NotStartedImpl> get copyWith =>
      __$$NotStartedImplCopyWithImpl<_$NotStartedImpl>(this, _$identity);

  @override
  @optionalTypeArgs
  TResult when<TResult extends Object?>({
    required TResult Function(String? syncTrigger, DateTime? lastSuccessfulSync)
        success,
    required TResult Function(String? syncTrigger, DateTime? lastSuccessfulSync)
        inProgress,
    required TResult Function(
            String message, String? syncTrigger, DateTime? lastSuccessfulSync)
        failed,
    required TResult Function(String? syncTrigger, DateTime? lastSuccessfulSync)
        notStarted,
    required TResult Function(DateTime? lastSuccessfulSync) deleting,
    required TResult Function(String message, DateTime? lastSuccessfulSync)
        deletionFailed,
  }) {
    return notStarted(syncTrigger, lastSuccessfulSync);
  }

  @override
  @optionalTypeArgs
  TResult? whenOrNull<TResult extends Object?>({
    TResult? Function(String? syncTrigger, DateTime? lastSuccessfulSync)?
        success,
    TResult? Function(String? syncTrigger, DateTime? lastSuccessfulSync)?
        inProgress,
    TResult? Function(
            String message, String? syncTrigger, DateTime? lastSuccessfulSync)?
        failed,
    TResult? Function(String? syncTrigger, DateTime? lastSuccessfulSync)?
        notStarted,
    TResult? Function(DateTime? lastSuccessfulSync)? deleting,
    TResult? Function(String message, DateTime? lastSuccessfulSync)?
        deletionFailed,
  }) {
    return notStarted?.call(syncTrigger, lastSuccessfulSync);
  }

  @override
  @optionalTypeArgs
  TResult maybeWhen<TResult extends Object?>({
    TResult Function(String? syncTrigger, DateTime? lastSuccessfulSync)?
        success,
    TResult Function(String? syncTrigger, DateTime? lastSuccessfulSync)?
        inProgress,
    TResult Function(
            String message, String? syncTrigger, DateTime? lastSuccessfulSync)?
        failed,
    TResult Function(String? syncTrigger, DateTime? lastSuccessfulSync)?
        notStarted,
    TResult Function(DateTime? lastSuccessfulSync)? deleting,
    TResult Function(String message, DateTime? lastSuccessfulSync)?
        deletionFailed,
    required TResult orElse(),
  }) {
    if (notStarted != null) {
      return notStarted(syncTrigger, lastSuccessfulSync);
    }
    return orElse();
  }

  @override
  @optionalTypeArgs
  TResult map<TResult extends Object?>({
    required TResult Function(_Success value) success,
    required TResult Function(_InProgress value) inProgress,
    required TResult Function(_Failed value) failed,
    required TResult Function(_NotStarted value) notStarted,
    required TResult Function(_Deleting value) deleting,
    required TResult Function(_DeletionFailed value) deletionFailed,
  }) {
    return notStarted(this);
  }

  @override
  @optionalTypeArgs
  TResult? mapOrNull<TResult extends Object?>({
    TResult? Function(_Success value)? success,
    TResult? Function(_InProgress value)? inProgress,
    TResult? Function(_Failed value)? failed,
    TResult? Function(_NotStarted value)? notStarted,
    TResult? Function(_Deleting value)? deleting,
    TResult? Function(_DeletionFailed value)? deletionFailed,
  }) {
    return notStarted?.call(this);
  }

  @override
  @optionalTypeArgs
  TResult maybeMap<TResult extends Object?>({
    TResult Function(_Success value)? success,
    TResult Function(_InProgress value)? inProgress,
    TResult Function(_Failed value)? failed,
    TResult Function(_NotStarted value)? notStarted,
    TResult Function(_Deleting value)? deleting,
    TResult Function(_DeletionFailed value)? deletionFailed,
    required TResult orElse(),
  }) {
    if (notStarted != null) {
      return notStarted(this);
    }
    return orElse();
  }
}

abstract class _NotStarted extends SyncProfileStatus {
  const factory _NotStarted(
      {final String? syncTrigger,
      final DateTime? lastSuccessfulSync}) = _$NotStartedImpl;
  const _NotStarted._() : super._();

  String? get syncTrigger;
  @override
  DateTime? get lastSuccessfulSync;
  @override
  @JsonKey(ignore: true)
  _$$NotStartedImplCopyWith<_$NotStartedImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class _$$DeletingImplCopyWith<$Res>
    implements $SyncProfileStatusCopyWith<$Res> {
  factory _$$DeletingImplCopyWith(
          _$DeletingImpl value, $Res Function(_$DeletingImpl) then) =
      __$$DeletingImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({DateTime? lastSuccessfulSync});
}

/// @nodoc
class __$$DeletingImplCopyWithImpl<$Res>
    extends _$SyncProfileStatusCopyWithImpl<$Res, _$DeletingImpl>
    implements _$$DeletingImplCopyWith<$Res> {
  __$$DeletingImplCopyWithImpl(
      _$DeletingImpl _value, $Res Function(_$DeletingImpl) _then)
      : super(_value, _then);

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? lastSuccessfulSync = freezed,
  }) {
    return _then(_$DeletingImpl(
      lastSuccessfulSync: freezed == lastSuccessfulSync
          ? _value.lastSuccessfulSync
          : lastSuccessfulSync // ignore: cast_nullable_to_non_nullable
              as DateTime?,
    ));
  }
}

/// @nodoc

class _$DeletingImpl extends _Deleting {
  const _$DeletingImpl({this.lastSuccessfulSync}) : super._();

  @override
  final DateTime? lastSuccessfulSync;

  @override
  String toString() {
    return 'SyncProfileStatus.deleting(lastSuccessfulSync: $lastSuccessfulSync)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$DeletingImpl &&
            (identical(other.lastSuccessfulSync, lastSuccessfulSync) ||
                other.lastSuccessfulSync == lastSuccessfulSync));
  }

  @override
  int get hashCode => Object.hash(runtimeType, lastSuccessfulSync);

  @JsonKey(ignore: true)
  @override
  @pragma('vm:prefer-inline')
  _$$DeletingImplCopyWith<_$DeletingImpl> get copyWith =>
      __$$DeletingImplCopyWithImpl<_$DeletingImpl>(this, _$identity);

  @override
  @optionalTypeArgs
  TResult when<TResult extends Object?>({
    required TResult Function(String? syncTrigger, DateTime? lastSuccessfulSync)
        success,
    required TResult Function(String? syncTrigger, DateTime? lastSuccessfulSync)
        inProgress,
    required TResult Function(
            String message, String? syncTrigger, DateTime? lastSuccessfulSync)
        failed,
    required TResult Function(String? syncTrigger, DateTime? lastSuccessfulSync)
        notStarted,
    required TResult Function(DateTime? lastSuccessfulSync) deleting,
    required TResult Function(String message, DateTime? lastSuccessfulSync)
        deletionFailed,
  }) {
    return deleting(lastSuccessfulSync);
  }

  @override
  @optionalTypeArgs
  TResult? whenOrNull<TResult extends Object?>({
    TResult? Function(String? syncTrigger, DateTime? lastSuccessfulSync)?
        success,
    TResult? Function(String? syncTrigger, DateTime? lastSuccessfulSync)?
        inProgress,
    TResult? Function(
            String message, String? syncTrigger, DateTime? lastSuccessfulSync)?
        failed,
    TResult? Function(String? syncTrigger, DateTime? lastSuccessfulSync)?
        notStarted,
    TResult? Function(DateTime? lastSuccessfulSync)? deleting,
    TResult? Function(String message, DateTime? lastSuccessfulSync)?
        deletionFailed,
  }) {
    return deleting?.call(lastSuccessfulSync);
  }

  @override
  @optionalTypeArgs
  TResult maybeWhen<TResult extends Object?>({
    TResult Function(String? syncTrigger, DateTime? lastSuccessfulSync)?
        success,
    TResult Function(String? syncTrigger, DateTime? lastSuccessfulSync)?
        inProgress,
    TResult Function(
            String message, String? syncTrigger, DateTime? lastSuccessfulSync)?
        failed,
    TResult Function(String? syncTrigger, DateTime? lastSuccessfulSync)?
        notStarted,
    TResult Function(DateTime? lastSuccessfulSync)? deleting,
    TResult Function(String message, DateTime? lastSuccessfulSync)?
        deletionFailed,
    required TResult orElse(),
  }) {
    if (deleting != null) {
      return deleting(lastSuccessfulSync);
    }
    return orElse();
  }

  @override
  @optionalTypeArgs
  TResult map<TResult extends Object?>({
    required TResult Function(_Success value) success,
    required TResult Function(_InProgress value) inProgress,
    required TResult Function(_Failed value) failed,
    required TResult Function(_NotStarted value) notStarted,
    required TResult Function(_Deleting value) deleting,
    required TResult Function(_DeletionFailed value) deletionFailed,
  }) {
    return deleting(this);
  }

  @override
  @optionalTypeArgs
  TResult? mapOrNull<TResult extends Object?>({
    TResult? Function(_Success value)? success,
    TResult? Function(_InProgress value)? inProgress,
    TResult? Function(_Failed value)? failed,
    TResult? Function(_NotStarted value)? notStarted,
    TResult? Function(_Deleting value)? deleting,
    TResult? Function(_DeletionFailed value)? deletionFailed,
  }) {
    return deleting?.call(this);
  }

  @override
  @optionalTypeArgs
  TResult maybeMap<TResult extends Object?>({
    TResult Function(_Success value)? success,
    TResult Function(_InProgress value)? inProgress,
    TResult Function(_Failed value)? failed,
    TResult Function(_NotStarted value)? notStarted,
    TResult Function(_Deleting value)? deleting,
    TResult Function(_DeletionFailed value)? deletionFailed,
    required TResult orElse(),
  }) {
    if (deleting != null) {
      return deleting(this);
    }
    return orElse();
  }
}

abstract class _Deleting extends SyncProfileStatus {
  const factory _Deleting({final DateTime? lastSuccessfulSync}) =
      _$DeletingImpl;
  const _Deleting._() : super._();

  @override
  DateTime? get lastSuccessfulSync;
  @override
  @JsonKey(ignore: true)
  _$$DeletingImplCopyWith<_$DeletingImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class _$$DeletionFailedImplCopyWith<$Res>
    implements $SyncProfileStatusCopyWith<$Res> {
  factory _$$DeletionFailedImplCopyWith(_$DeletionFailedImpl value,
          $Res Function(_$DeletionFailedImpl) then) =
      __$$DeletionFailedImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({String message, DateTime? lastSuccessfulSync});
}

/// @nodoc
class __$$DeletionFailedImplCopyWithImpl<$Res>
    extends _$SyncProfileStatusCopyWithImpl<$Res, _$DeletionFailedImpl>
    implements _$$DeletionFailedImplCopyWith<$Res> {
  __$$DeletionFailedImplCopyWithImpl(
      _$DeletionFailedImpl _value, $Res Function(_$DeletionFailedImpl) _then)
      : super(_value, _then);

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? message = null,
    Object? lastSuccessfulSync = freezed,
  }) {
    return _then(_$DeletionFailedImpl(
      null == message
          ? _value.message
          : message // ignore: cast_nullable_to_non_nullable
              as String,
      lastSuccessfulSync: freezed == lastSuccessfulSync
          ? _value.lastSuccessfulSync
          : lastSuccessfulSync // ignore: cast_nullable_to_non_nullable
              as DateTime?,
    ));
  }
}

/// @nodoc

class _$DeletionFailedImpl extends _DeletionFailed {
  const _$DeletionFailedImpl(this.message, {this.lastSuccessfulSync})
      : super._();

  @override
  final String message;
  @override
  final DateTime? lastSuccessfulSync;

  @override
  String toString() {
    return 'SyncProfileStatus.deletionFailed(message: $message, lastSuccessfulSync: $lastSuccessfulSync)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$DeletionFailedImpl &&
            (identical(other.message, message) || other.message == message) &&
            (identical(other.lastSuccessfulSync, lastSuccessfulSync) ||
                other.lastSuccessfulSync == lastSuccessfulSync));
  }

  @override
  int get hashCode => Object.hash(runtimeType, message, lastSuccessfulSync);

  @JsonKey(ignore: true)
  @override
  @pragma('vm:prefer-inline')
  _$$DeletionFailedImplCopyWith<_$DeletionFailedImpl> get copyWith =>
      __$$DeletionFailedImplCopyWithImpl<_$DeletionFailedImpl>(
          this, _$identity);

  @override
  @optionalTypeArgs
  TResult when<TResult extends Object?>({
    required TResult Function(String? syncTrigger, DateTime? lastSuccessfulSync)
        success,
    required TResult Function(String? syncTrigger, DateTime? lastSuccessfulSync)
        inProgress,
    required TResult Function(
            String message, String? syncTrigger, DateTime? lastSuccessfulSync)
        failed,
    required TResult Function(String? syncTrigger, DateTime? lastSuccessfulSync)
        notStarted,
    required TResult Function(DateTime? lastSuccessfulSync) deleting,
    required TResult Function(String message, DateTime? lastSuccessfulSync)
        deletionFailed,
  }) {
    return deletionFailed(message, lastSuccessfulSync);
  }

  @override
  @optionalTypeArgs
  TResult? whenOrNull<TResult extends Object?>({
    TResult? Function(String? syncTrigger, DateTime? lastSuccessfulSync)?
        success,
    TResult? Function(String? syncTrigger, DateTime? lastSuccessfulSync)?
        inProgress,
    TResult? Function(
            String message, String? syncTrigger, DateTime? lastSuccessfulSync)?
        failed,
    TResult? Function(String? syncTrigger, DateTime? lastSuccessfulSync)?
        notStarted,
    TResult? Function(DateTime? lastSuccessfulSync)? deleting,
    TResult? Function(String message, DateTime? lastSuccessfulSync)?
        deletionFailed,
  }) {
    return deletionFailed?.call(message, lastSuccessfulSync);
  }

  @override
  @optionalTypeArgs
  TResult maybeWhen<TResult extends Object?>({
    TResult Function(String? syncTrigger, DateTime? lastSuccessfulSync)?
        success,
    TResult Function(String? syncTrigger, DateTime? lastSuccessfulSync)?
        inProgress,
    TResult Function(
            String message, String? syncTrigger, DateTime? lastSuccessfulSync)?
        failed,
    TResult Function(String? syncTrigger, DateTime? lastSuccessfulSync)?
        notStarted,
    TResult Function(DateTime? lastSuccessfulSync)? deleting,
    TResult Function(String message, DateTime? lastSuccessfulSync)?
        deletionFailed,
    required TResult orElse(),
  }) {
    if (deletionFailed != null) {
      return deletionFailed(message, lastSuccessfulSync);
    }
    return orElse();
  }

  @override
  @optionalTypeArgs
  TResult map<TResult extends Object?>({
    required TResult Function(_Success value) success,
    required TResult Function(_InProgress value) inProgress,
    required TResult Function(_Failed value) failed,
    required TResult Function(_NotStarted value) notStarted,
    required TResult Function(_Deleting value) deleting,
    required TResult Function(_DeletionFailed value) deletionFailed,
  }) {
    return deletionFailed(this);
  }

  @override
  @optionalTypeArgs
  TResult? mapOrNull<TResult extends Object?>({
    TResult? Function(_Success value)? success,
    TResult? Function(_InProgress value)? inProgress,
    TResult? Function(_Failed value)? failed,
    TResult? Function(_NotStarted value)? notStarted,
    TResult? Function(_Deleting value)? deleting,
    TResult? Function(_DeletionFailed value)? deletionFailed,
  }) {
    return deletionFailed?.call(this);
  }

  @override
  @optionalTypeArgs
  TResult maybeMap<TResult extends Object?>({
    TResult Function(_Success value)? success,
    TResult Function(_InProgress value)? inProgress,
    TResult Function(_Failed value)? failed,
    TResult Function(_NotStarted value)? notStarted,
    TResult Function(_Deleting value)? deleting,
    TResult Function(_DeletionFailed value)? deletionFailed,
    required TResult orElse(),
  }) {
    if (deletionFailed != null) {
      return deletionFailed(this);
    }
    return orElse();
  }
}

abstract class _DeletionFailed extends SyncProfileStatus {
  const factory _DeletionFailed(final String message,
      {final DateTime? lastSuccessfulSync}) = _$DeletionFailedImpl;
  const _DeletionFailed._() : super._();

  String get message;
  @override
  DateTime? get lastSuccessfulSync;
  @override
  @JsonKey(ignore: true)
  _$$DeletionFailedImplCopyWith<_$DeletionFailedImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
