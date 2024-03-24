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
  @optionalTypeArgs
  TResult when<TResult extends Object?>({
    required TResult Function() success,
    required TResult Function() inProgress,
    required TResult Function(String message) failed,
    required TResult Function() notStarted,
  }) =>
      throw _privateConstructorUsedError;
  @optionalTypeArgs
  TResult? whenOrNull<TResult extends Object?>({
    TResult? Function()? success,
    TResult? Function()? inProgress,
    TResult? Function(String message)? failed,
    TResult? Function()? notStarted,
  }) =>
      throw _privateConstructorUsedError;
  @optionalTypeArgs
  TResult maybeWhen<TResult extends Object?>({
    TResult Function()? success,
    TResult Function()? inProgress,
    TResult Function(String message)? failed,
    TResult Function()? notStarted,
    required TResult orElse(),
  }) =>
      throw _privateConstructorUsedError;
  @optionalTypeArgs
  TResult map<TResult extends Object?>({
    required TResult Function(_Success value) success,
    required TResult Function(_InProgress value) inProgress,
    required TResult Function(_Failed value) failed,
    required TResult Function(_NotStarted value) notStarted,
  }) =>
      throw _privateConstructorUsedError;
  @optionalTypeArgs
  TResult? mapOrNull<TResult extends Object?>({
    TResult? Function(_Success value)? success,
    TResult? Function(_InProgress value)? inProgress,
    TResult? Function(_Failed value)? failed,
    TResult? Function(_NotStarted value)? notStarted,
  }) =>
      throw _privateConstructorUsedError;
  @optionalTypeArgs
  TResult maybeMap<TResult extends Object?>({
    TResult Function(_Success value)? success,
    TResult Function(_InProgress value)? inProgress,
    TResult Function(_Failed value)? failed,
    TResult Function(_NotStarted value)? notStarted,
    required TResult orElse(),
  }) =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $SyncProfileStatusCopyWith<$Res> {
  factory $SyncProfileStatusCopyWith(
          SyncProfileStatus value, $Res Function(SyncProfileStatus) then) =
      _$SyncProfileStatusCopyWithImpl<$Res, SyncProfileStatus>;
}

/// @nodoc
class _$SyncProfileStatusCopyWithImpl<$Res, $Val extends SyncProfileStatus>
    implements $SyncProfileStatusCopyWith<$Res> {
  _$SyncProfileStatusCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;
}

/// @nodoc
abstract class _$$SuccessImplCopyWith<$Res> {
  factory _$$SuccessImplCopyWith(
          _$SuccessImpl value, $Res Function(_$SuccessImpl) then) =
      __$$SuccessImplCopyWithImpl<$Res>;
}

/// @nodoc
class __$$SuccessImplCopyWithImpl<$Res>
    extends _$SyncProfileStatusCopyWithImpl<$Res, _$SuccessImpl>
    implements _$$SuccessImplCopyWith<$Res> {
  __$$SuccessImplCopyWithImpl(
      _$SuccessImpl _value, $Res Function(_$SuccessImpl) _then)
      : super(_value, _then);
}

/// @nodoc

class _$SuccessImpl extends _Success {
  const _$SuccessImpl() : super._();

  @override
  String toString() {
    return 'SyncProfileStatus.success()';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType && other is _$SuccessImpl);
  }

  @override
  int get hashCode => runtimeType.hashCode;

  @override
  @optionalTypeArgs
  TResult when<TResult extends Object?>({
    required TResult Function() success,
    required TResult Function() inProgress,
    required TResult Function(String message) failed,
    required TResult Function() notStarted,
  }) {
    return success();
  }

  @override
  @optionalTypeArgs
  TResult? whenOrNull<TResult extends Object?>({
    TResult? Function()? success,
    TResult? Function()? inProgress,
    TResult? Function(String message)? failed,
    TResult? Function()? notStarted,
  }) {
    return success?.call();
  }

  @override
  @optionalTypeArgs
  TResult maybeWhen<TResult extends Object?>({
    TResult Function()? success,
    TResult Function()? inProgress,
    TResult Function(String message)? failed,
    TResult Function()? notStarted,
    required TResult orElse(),
  }) {
    if (success != null) {
      return success();
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
    required TResult orElse(),
  }) {
    if (success != null) {
      return success(this);
    }
    return orElse();
  }
}

abstract class _Success extends SyncProfileStatus {
  const factory _Success() = _$SuccessImpl;
  const _Success._() : super._();
}

/// @nodoc
abstract class _$$InProgressImplCopyWith<$Res> {
  factory _$$InProgressImplCopyWith(
          _$InProgressImpl value, $Res Function(_$InProgressImpl) then) =
      __$$InProgressImplCopyWithImpl<$Res>;
}

/// @nodoc
class __$$InProgressImplCopyWithImpl<$Res>
    extends _$SyncProfileStatusCopyWithImpl<$Res, _$InProgressImpl>
    implements _$$InProgressImplCopyWith<$Res> {
  __$$InProgressImplCopyWithImpl(
      _$InProgressImpl _value, $Res Function(_$InProgressImpl) _then)
      : super(_value, _then);
}

/// @nodoc

class _$InProgressImpl extends _InProgress {
  const _$InProgressImpl() : super._();

  @override
  String toString() {
    return 'SyncProfileStatus.inProgress()';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType && other is _$InProgressImpl);
  }

  @override
  int get hashCode => runtimeType.hashCode;

  @override
  @optionalTypeArgs
  TResult when<TResult extends Object?>({
    required TResult Function() success,
    required TResult Function() inProgress,
    required TResult Function(String message) failed,
    required TResult Function() notStarted,
  }) {
    return inProgress();
  }

  @override
  @optionalTypeArgs
  TResult? whenOrNull<TResult extends Object?>({
    TResult? Function()? success,
    TResult? Function()? inProgress,
    TResult? Function(String message)? failed,
    TResult? Function()? notStarted,
  }) {
    return inProgress?.call();
  }

  @override
  @optionalTypeArgs
  TResult maybeWhen<TResult extends Object?>({
    TResult Function()? success,
    TResult Function()? inProgress,
    TResult Function(String message)? failed,
    TResult Function()? notStarted,
    required TResult orElse(),
  }) {
    if (inProgress != null) {
      return inProgress();
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
    required TResult orElse(),
  }) {
    if (inProgress != null) {
      return inProgress(this);
    }
    return orElse();
  }
}

abstract class _InProgress extends SyncProfileStatus {
  const factory _InProgress() = _$InProgressImpl;
  const _InProgress._() : super._();
}

/// @nodoc
abstract class _$$FailedImplCopyWith<$Res> {
  factory _$$FailedImplCopyWith(
          _$FailedImpl value, $Res Function(_$FailedImpl) then) =
      __$$FailedImplCopyWithImpl<$Res>;
  @useResult
  $Res call({String message});
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
  }) {
    return _then(_$FailedImpl(
      null == message
          ? _value.message
          : message // ignore: cast_nullable_to_non_nullable
              as String,
    ));
  }
}

/// @nodoc

class _$FailedImpl extends _Failed {
  const _$FailedImpl(this.message) : super._();

  @override
  final String message;

  @override
  String toString() {
    return 'SyncProfileStatus.failed(message: $message)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$FailedImpl &&
            (identical(other.message, message) || other.message == message));
  }

  @override
  int get hashCode => Object.hash(runtimeType, message);

  @JsonKey(ignore: true)
  @override
  @pragma('vm:prefer-inline')
  _$$FailedImplCopyWith<_$FailedImpl> get copyWith =>
      __$$FailedImplCopyWithImpl<_$FailedImpl>(this, _$identity);

  @override
  @optionalTypeArgs
  TResult when<TResult extends Object?>({
    required TResult Function() success,
    required TResult Function() inProgress,
    required TResult Function(String message) failed,
    required TResult Function() notStarted,
  }) {
    return failed(message);
  }

  @override
  @optionalTypeArgs
  TResult? whenOrNull<TResult extends Object?>({
    TResult? Function()? success,
    TResult? Function()? inProgress,
    TResult? Function(String message)? failed,
    TResult? Function()? notStarted,
  }) {
    return failed?.call(message);
  }

  @override
  @optionalTypeArgs
  TResult maybeWhen<TResult extends Object?>({
    TResult Function()? success,
    TResult Function()? inProgress,
    TResult Function(String message)? failed,
    TResult Function()? notStarted,
    required TResult orElse(),
  }) {
    if (failed != null) {
      return failed(message);
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
    required TResult orElse(),
  }) {
    if (failed != null) {
      return failed(this);
    }
    return orElse();
  }
}

abstract class _Failed extends SyncProfileStatus {
  const factory _Failed(final String message) = _$FailedImpl;
  const _Failed._() : super._();

  String get message;
  @JsonKey(ignore: true)
  _$$FailedImplCopyWith<_$FailedImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class _$$NotStartedImplCopyWith<$Res> {
  factory _$$NotStartedImplCopyWith(
          _$NotStartedImpl value, $Res Function(_$NotStartedImpl) then) =
      __$$NotStartedImplCopyWithImpl<$Res>;
}

/// @nodoc
class __$$NotStartedImplCopyWithImpl<$Res>
    extends _$SyncProfileStatusCopyWithImpl<$Res, _$NotStartedImpl>
    implements _$$NotStartedImplCopyWith<$Res> {
  __$$NotStartedImplCopyWithImpl(
      _$NotStartedImpl _value, $Res Function(_$NotStartedImpl) _then)
      : super(_value, _then);
}

/// @nodoc

class _$NotStartedImpl extends _NotStarted {
  const _$NotStartedImpl() : super._();

  @override
  String toString() {
    return 'SyncProfileStatus.notStarted()';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType && other is _$NotStartedImpl);
  }

  @override
  int get hashCode => runtimeType.hashCode;

  @override
  @optionalTypeArgs
  TResult when<TResult extends Object?>({
    required TResult Function() success,
    required TResult Function() inProgress,
    required TResult Function(String message) failed,
    required TResult Function() notStarted,
  }) {
    return notStarted();
  }

  @override
  @optionalTypeArgs
  TResult? whenOrNull<TResult extends Object?>({
    TResult? Function()? success,
    TResult? Function()? inProgress,
    TResult? Function(String message)? failed,
    TResult? Function()? notStarted,
  }) {
    return notStarted?.call();
  }

  @override
  @optionalTypeArgs
  TResult maybeWhen<TResult extends Object?>({
    TResult Function()? success,
    TResult Function()? inProgress,
    TResult Function(String message)? failed,
    TResult Function()? notStarted,
    required TResult orElse(),
  }) {
    if (notStarted != null) {
      return notStarted();
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
    required TResult orElse(),
  }) {
    if (notStarted != null) {
      return notStarted(this);
    }
    return orElse();
  }
}

abstract class _NotStarted extends SyncProfileStatus {
  const factory _NotStarted() = _$NotStartedImpl;
  const _NotStarted._() : super._();
}
