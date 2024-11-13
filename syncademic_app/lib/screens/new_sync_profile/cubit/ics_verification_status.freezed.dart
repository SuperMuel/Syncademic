// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'ics_verification_status.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

/// @nodoc
mixin _$IcsVerificationStatus {
  @optionalTypeArgs
  TResult when<TResult extends Object?>({
    required TResult Function() notVerified,
    required TResult Function() verificationInProgress,
    required TResult Function() verified,
    required TResult Function(String errorMessage) verificationFailed,
  }) =>
      throw _privateConstructorUsedError;
  @optionalTypeArgs
  TResult? whenOrNull<TResult extends Object?>({
    TResult? Function()? notVerified,
    TResult? Function()? verificationInProgress,
    TResult? Function()? verified,
    TResult? Function(String errorMessage)? verificationFailed,
  }) =>
      throw _privateConstructorUsedError;
  @optionalTypeArgs
  TResult maybeWhen<TResult extends Object?>({
    TResult Function()? notVerified,
    TResult Function()? verificationInProgress,
    TResult Function()? verified,
    TResult Function(String errorMessage)? verificationFailed,
    required TResult orElse(),
  }) =>
      throw _privateConstructorUsedError;
  @optionalTypeArgs
  TResult map<TResult extends Object?>({
    required TResult Function(NotVerified value) notVerified,
    required TResult Function(VerificationInProgress value)
        verificationInProgress,
    required TResult Function(Verified value) verified,
    required TResult Function(VerificationFailed value) verificationFailed,
  }) =>
      throw _privateConstructorUsedError;
  @optionalTypeArgs
  TResult? mapOrNull<TResult extends Object?>({
    TResult? Function(NotVerified value)? notVerified,
    TResult? Function(VerificationInProgress value)? verificationInProgress,
    TResult? Function(Verified value)? verified,
    TResult? Function(VerificationFailed value)? verificationFailed,
  }) =>
      throw _privateConstructorUsedError;
  @optionalTypeArgs
  TResult maybeMap<TResult extends Object?>({
    TResult Function(NotVerified value)? notVerified,
    TResult Function(VerificationInProgress value)? verificationInProgress,
    TResult Function(Verified value)? verified,
    TResult Function(VerificationFailed value)? verificationFailed,
    required TResult orElse(),
  }) =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $IcsVerificationStatusCopyWith<$Res> {
  factory $IcsVerificationStatusCopyWith(IcsVerificationStatus value,
          $Res Function(IcsVerificationStatus) then) =
      _$IcsVerificationStatusCopyWithImpl<$Res, IcsVerificationStatus>;
}

/// @nodoc
class _$IcsVerificationStatusCopyWithImpl<$Res,
        $Val extends IcsVerificationStatus>
    implements $IcsVerificationStatusCopyWith<$Res> {
  _$IcsVerificationStatusCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;
}

/// @nodoc
abstract class _$$NotVerifiedImplCopyWith<$Res> {
  factory _$$NotVerifiedImplCopyWith(
          _$NotVerifiedImpl value, $Res Function(_$NotVerifiedImpl) then) =
      __$$NotVerifiedImplCopyWithImpl<$Res>;
}

/// @nodoc
class __$$NotVerifiedImplCopyWithImpl<$Res>
    extends _$IcsVerificationStatusCopyWithImpl<$Res, _$NotVerifiedImpl>
    implements _$$NotVerifiedImplCopyWith<$Res> {
  __$$NotVerifiedImplCopyWithImpl(
      _$NotVerifiedImpl _value, $Res Function(_$NotVerifiedImpl) _then)
      : super(_value, _then);
}

/// @nodoc

class _$NotVerifiedImpl extends NotVerified {
  const _$NotVerifiedImpl() : super._();

  @override
  String toString() {
    return 'IcsVerificationStatus.notVerified()';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType && other is _$NotVerifiedImpl);
  }

  @override
  int get hashCode => runtimeType.hashCode;

  @override
  @optionalTypeArgs
  TResult when<TResult extends Object?>({
    required TResult Function() notVerified,
    required TResult Function() verificationInProgress,
    required TResult Function() verified,
    required TResult Function(String errorMessage) verificationFailed,
  }) {
    return notVerified();
  }

  @override
  @optionalTypeArgs
  TResult? whenOrNull<TResult extends Object?>({
    TResult? Function()? notVerified,
    TResult? Function()? verificationInProgress,
    TResult? Function()? verified,
    TResult? Function(String errorMessage)? verificationFailed,
  }) {
    return notVerified?.call();
  }

  @override
  @optionalTypeArgs
  TResult maybeWhen<TResult extends Object?>({
    TResult Function()? notVerified,
    TResult Function()? verificationInProgress,
    TResult Function()? verified,
    TResult Function(String errorMessage)? verificationFailed,
    required TResult orElse(),
  }) {
    if (notVerified != null) {
      return notVerified();
    }
    return orElse();
  }

  @override
  @optionalTypeArgs
  TResult map<TResult extends Object?>({
    required TResult Function(NotVerified value) notVerified,
    required TResult Function(VerificationInProgress value)
        verificationInProgress,
    required TResult Function(Verified value) verified,
    required TResult Function(VerificationFailed value) verificationFailed,
  }) {
    return notVerified(this);
  }

  @override
  @optionalTypeArgs
  TResult? mapOrNull<TResult extends Object?>({
    TResult? Function(NotVerified value)? notVerified,
    TResult? Function(VerificationInProgress value)? verificationInProgress,
    TResult? Function(Verified value)? verified,
    TResult? Function(VerificationFailed value)? verificationFailed,
  }) {
    return notVerified?.call(this);
  }

  @override
  @optionalTypeArgs
  TResult maybeMap<TResult extends Object?>({
    TResult Function(NotVerified value)? notVerified,
    TResult Function(VerificationInProgress value)? verificationInProgress,
    TResult Function(Verified value)? verified,
    TResult Function(VerificationFailed value)? verificationFailed,
    required TResult orElse(),
  }) {
    if (notVerified != null) {
      return notVerified(this);
    }
    return orElse();
  }
}

abstract class NotVerified extends IcsVerificationStatus {
  const factory NotVerified() = _$NotVerifiedImpl;
  const NotVerified._() : super._();
}

/// @nodoc
abstract class _$$VerificationInProgressImplCopyWith<$Res> {
  factory _$$VerificationInProgressImplCopyWith(
          _$VerificationInProgressImpl value,
          $Res Function(_$VerificationInProgressImpl) then) =
      __$$VerificationInProgressImplCopyWithImpl<$Res>;
}

/// @nodoc
class __$$VerificationInProgressImplCopyWithImpl<$Res>
    extends _$IcsVerificationStatusCopyWithImpl<$Res,
        _$VerificationInProgressImpl>
    implements _$$VerificationInProgressImplCopyWith<$Res> {
  __$$VerificationInProgressImplCopyWithImpl(
      _$VerificationInProgressImpl _value,
      $Res Function(_$VerificationInProgressImpl) _then)
      : super(_value, _then);
}

/// @nodoc

class _$VerificationInProgressImpl extends VerificationInProgress {
  const _$VerificationInProgressImpl() : super._();

  @override
  String toString() {
    return 'IcsVerificationStatus.verificationInProgress()';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$VerificationInProgressImpl);
  }

  @override
  int get hashCode => runtimeType.hashCode;

  @override
  @optionalTypeArgs
  TResult when<TResult extends Object?>({
    required TResult Function() notVerified,
    required TResult Function() verificationInProgress,
    required TResult Function() verified,
    required TResult Function(String errorMessage) verificationFailed,
  }) {
    return verificationInProgress();
  }

  @override
  @optionalTypeArgs
  TResult? whenOrNull<TResult extends Object?>({
    TResult? Function()? notVerified,
    TResult? Function()? verificationInProgress,
    TResult? Function()? verified,
    TResult? Function(String errorMessage)? verificationFailed,
  }) {
    return verificationInProgress?.call();
  }

  @override
  @optionalTypeArgs
  TResult maybeWhen<TResult extends Object?>({
    TResult Function()? notVerified,
    TResult Function()? verificationInProgress,
    TResult Function()? verified,
    TResult Function(String errorMessage)? verificationFailed,
    required TResult orElse(),
  }) {
    if (verificationInProgress != null) {
      return verificationInProgress();
    }
    return orElse();
  }

  @override
  @optionalTypeArgs
  TResult map<TResult extends Object?>({
    required TResult Function(NotVerified value) notVerified,
    required TResult Function(VerificationInProgress value)
        verificationInProgress,
    required TResult Function(Verified value) verified,
    required TResult Function(VerificationFailed value) verificationFailed,
  }) {
    return verificationInProgress(this);
  }

  @override
  @optionalTypeArgs
  TResult? mapOrNull<TResult extends Object?>({
    TResult? Function(NotVerified value)? notVerified,
    TResult? Function(VerificationInProgress value)? verificationInProgress,
    TResult? Function(Verified value)? verified,
    TResult? Function(VerificationFailed value)? verificationFailed,
  }) {
    return verificationInProgress?.call(this);
  }

  @override
  @optionalTypeArgs
  TResult maybeMap<TResult extends Object?>({
    TResult Function(NotVerified value)? notVerified,
    TResult Function(VerificationInProgress value)? verificationInProgress,
    TResult Function(Verified value)? verified,
    TResult Function(VerificationFailed value)? verificationFailed,
    required TResult orElse(),
  }) {
    if (verificationInProgress != null) {
      return verificationInProgress(this);
    }
    return orElse();
  }
}

abstract class VerificationInProgress extends IcsVerificationStatus {
  const factory VerificationInProgress() = _$VerificationInProgressImpl;
  const VerificationInProgress._() : super._();
}

/// @nodoc
abstract class _$$VerifiedImplCopyWith<$Res> {
  factory _$$VerifiedImplCopyWith(
          _$VerifiedImpl value, $Res Function(_$VerifiedImpl) then) =
      __$$VerifiedImplCopyWithImpl<$Res>;
}

/// @nodoc
class __$$VerifiedImplCopyWithImpl<$Res>
    extends _$IcsVerificationStatusCopyWithImpl<$Res, _$VerifiedImpl>
    implements _$$VerifiedImplCopyWith<$Res> {
  __$$VerifiedImplCopyWithImpl(
      _$VerifiedImpl _value, $Res Function(_$VerifiedImpl) _then)
      : super(_value, _then);
}

/// @nodoc

class _$VerifiedImpl extends Verified {
  const _$VerifiedImpl() : super._();

  @override
  String toString() {
    return 'IcsVerificationStatus.verified()';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType && other is _$VerifiedImpl);
  }

  @override
  int get hashCode => runtimeType.hashCode;

  @override
  @optionalTypeArgs
  TResult when<TResult extends Object?>({
    required TResult Function() notVerified,
    required TResult Function() verificationInProgress,
    required TResult Function() verified,
    required TResult Function(String errorMessage) verificationFailed,
  }) {
    return verified();
  }

  @override
  @optionalTypeArgs
  TResult? whenOrNull<TResult extends Object?>({
    TResult? Function()? notVerified,
    TResult? Function()? verificationInProgress,
    TResult? Function()? verified,
    TResult? Function(String errorMessage)? verificationFailed,
  }) {
    return verified?.call();
  }

  @override
  @optionalTypeArgs
  TResult maybeWhen<TResult extends Object?>({
    TResult Function()? notVerified,
    TResult Function()? verificationInProgress,
    TResult Function()? verified,
    TResult Function(String errorMessage)? verificationFailed,
    required TResult orElse(),
  }) {
    if (verified != null) {
      return verified();
    }
    return orElse();
  }

  @override
  @optionalTypeArgs
  TResult map<TResult extends Object?>({
    required TResult Function(NotVerified value) notVerified,
    required TResult Function(VerificationInProgress value)
        verificationInProgress,
    required TResult Function(Verified value) verified,
    required TResult Function(VerificationFailed value) verificationFailed,
  }) {
    return verified(this);
  }

  @override
  @optionalTypeArgs
  TResult? mapOrNull<TResult extends Object?>({
    TResult? Function(NotVerified value)? notVerified,
    TResult? Function(VerificationInProgress value)? verificationInProgress,
    TResult? Function(Verified value)? verified,
    TResult? Function(VerificationFailed value)? verificationFailed,
  }) {
    return verified?.call(this);
  }

  @override
  @optionalTypeArgs
  TResult maybeMap<TResult extends Object?>({
    TResult Function(NotVerified value)? notVerified,
    TResult Function(VerificationInProgress value)? verificationInProgress,
    TResult Function(Verified value)? verified,
    TResult Function(VerificationFailed value)? verificationFailed,
    required TResult orElse(),
  }) {
    if (verified != null) {
      return verified(this);
    }
    return orElse();
  }
}

abstract class Verified extends IcsVerificationStatus {
  const factory Verified() = _$VerifiedImpl;
  const Verified._() : super._();
}

/// @nodoc
abstract class _$$VerificationFailedImplCopyWith<$Res> {
  factory _$$VerificationFailedImplCopyWith(_$VerificationFailedImpl value,
          $Res Function(_$VerificationFailedImpl) then) =
      __$$VerificationFailedImplCopyWithImpl<$Res>;
  @useResult
  $Res call({String errorMessage});
}

/// @nodoc
class __$$VerificationFailedImplCopyWithImpl<$Res>
    extends _$IcsVerificationStatusCopyWithImpl<$Res, _$VerificationFailedImpl>
    implements _$$VerificationFailedImplCopyWith<$Res> {
  __$$VerificationFailedImplCopyWithImpl(_$VerificationFailedImpl _value,
      $Res Function(_$VerificationFailedImpl) _then)
      : super(_value, _then);

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? errorMessage = null,
  }) {
    return _then(_$VerificationFailedImpl(
      errorMessage: null == errorMessage
          ? _value.errorMessage
          : errorMessage // ignore: cast_nullable_to_non_nullable
              as String,
    ));
  }
}

/// @nodoc

class _$VerificationFailedImpl extends VerificationFailed {
  const _$VerificationFailedImpl({required this.errorMessage}) : super._();

  @override
  final String errorMessage;

  @override
  String toString() {
    return 'IcsVerificationStatus.verificationFailed(errorMessage: $errorMessage)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$VerificationFailedImpl &&
            (identical(other.errorMessage, errorMessage) ||
                other.errorMessage == errorMessage));
  }

  @override
  int get hashCode => Object.hash(runtimeType, errorMessage);

  @JsonKey(ignore: true)
  @override
  @pragma('vm:prefer-inline')
  _$$VerificationFailedImplCopyWith<_$VerificationFailedImpl> get copyWith =>
      __$$VerificationFailedImplCopyWithImpl<_$VerificationFailedImpl>(
          this, _$identity);

  @override
  @optionalTypeArgs
  TResult when<TResult extends Object?>({
    required TResult Function() notVerified,
    required TResult Function() verificationInProgress,
    required TResult Function() verified,
    required TResult Function(String errorMessage) verificationFailed,
  }) {
    return verificationFailed(errorMessage);
  }

  @override
  @optionalTypeArgs
  TResult? whenOrNull<TResult extends Object?>({
    TResult? Function()? notVerified,
    TResult? Function()? verificationInProgress,
    TResult? Function()? verified,
    TResult? Function(String errorMessage)? verificationFailed,
  }) {
    return verificationFailed?.call(errorMessage);
  }

  @override
  @optionalTypeArgs
  TResult maybeWhen<TResult extends Object?>({
    TResult Function()? notVerified,
    TResult Function()? verificationInProgress,
    TResult Function()? verified,
    TResult Function(String errorMessage)? verificationFailed,
    required TResult orElse(),
  }) {
    if (verificationFailed != null) {
      return verificationFailed(errorMessage);
    }
    return orElse();
  }

  @override
  @optionalTypeArgs
  TResult map<TResult extends Object?>({
    required TResult Function(NotVerified value) notVerified,
    required TResult Function(VerificationInProgress value)
        verificationInProgress,
    required TResult Function(Verified value) verified,
    required TResult Function(VerificationFailed value) verificationFailed,
  }) {
    return verificationFailed(this);
  }

  @override
  @optionalTypeArgs
  TResult? mapOrNull<TResult extends Object?>({
    TResult? Function(NotVerified value)? notVerified,
    TResult? Function(VerificationInProgress value)? verificationInProgress,
    TResult? Function(Verified value)? verified,
    TResult? Function(VerificationFailed value)? verificationFailed,
  }) {
    return verificationFailed?.call(this);
  }

  @override
  @optionalTypeArgs
  TResult maybeMap<TResult extends Object?>({
    TResult Function(NotVerified value)? notVerified,
    TResult Function(VerificationInProgress value)? verificationInProgress,
    TResult Function(Verified value)? verified,
    TResult Function(VerificationFailed value)? verificationFailed,
    required TResult orElse(),
  }) {
    if (verificationFailed != null) {
      return verificationFailed(this);
    }
    return orElse();
  }
}

abstract class VerificationFailed extends IcsVerificationStatus {
  const factory VerificationFailed({required final String errorMessage}) =
      _$VerificationFailedImpl;
  const VerificationFailed._() : super._();

  String get errorMessage;
  @JsonKey(ignore: true)
  _$$VerificationFailedImplCopyWith<_$VerificationFailedImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
