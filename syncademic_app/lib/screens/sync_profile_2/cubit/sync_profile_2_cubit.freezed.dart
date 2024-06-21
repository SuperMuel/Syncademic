// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'sync_profile_2_cubit.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

/// @nodoc
mixin _$SyncProfile_2State {
  SyncProfile get syncProfile => throw _privateConstructorUsedError;
  bool get canRequestSync => throw _privateConstructorUsedError;

  @JsonKey(ignore: true)
  $SyncProfile_2StateCopyWith<SyncProfile_2State> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $SyncProfile_2StateCopyWith<$Res> {
  factory $SyncProfile_2StateCopyWith(
          SyncProfile_2State value, $Res Function(SyncProfile_2State) then) =
      _$SyncProfile_2StateCopyWithImpl<$Res, SyncProfile_2State>;
  @useResult
  $Res call({SyncProfile syncProfile, bool canRequestSync});

  $SyncProfileCopyWith<$Res> get syncProfile;
}

/// @nodoc
class _$SyncProfile_2StateCopyWithImpl<$Res, $Val extends SyncProfile_2State>
    implements $SyncProfile_2StateCopyWith<$Res> {
  _$SyncProfile_2StateCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? syncProfile = null,
    Object? canRequestSync = null,
  }) {
    return _then(_value.copyWith(
      syncProfile: null == syncProfile
          ? _value.syncProfile
          : syncProfile // ignore: cast_nullable_to_non_nullable
              as SyncProfile,
      canRequestSync: null == canRequestSync
          ? _value.canRequestSync
          : canRequestSync // ignore: cast_nullable_to_non_nullable
              as bool,
    ) as $Val);
  }

  @override
  @pragma('vm:prefer-inline')
  $SyncProfileCopyWith<$Res> get syncProfile {
    return $SyncProfileCopyWith<$Res>(_value.syncProfile, (value) {
      return _then(_value.copyWith(syncProfile: value) as $Val);
    });
  }
}

/// @nodoc
abstract class _$$SyncProfile_2StateImplCopyWith<$Res>
    implements $SyncProfile_2StateCopyWith<$Res> {
  factory _$$SyncProfile_2StateImplCopyWith(_$SyncProfile_2StateImpl value,
          $Res Function(_$SyncProfile_2StateImpl) then) =
      __$$SyncProfile_2StateImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({SyncProfile syncProfile, bool canRequestSync});

  @override
  $SyncProfileCopyWith<$Res> get syncProfile;
}

/// @nodoc
class __$$SyncProfile_2StateImplCopyWithImpl<$Res>
    extends _$SyncProfile_2StateCopyWithImpl<$Res, _$SyncProfile_2StateImpl>
    implements _$$SyncProfile_2StateImplCopyWith<$Res> {
  __$$SyncProfile_2StateImplCopyWithImpl(_$SyncProfile_2StateImpl _value,
      $Res Function(_$SyncProfile_2StateImpl) _then)
      : super(_value, _then);

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? syncProfile = null,
    Object? canRequestSync = null,
  }) {
    return _then(_$SyncProfile_2StateImpl(
      syncProfile: null == syncProfile
          ? _value.syncProfile
          : syncProfile // ignore: cast_nullable_to_non_nullable
              as SyncProfile,
      canRequestSync: null == canRequestSync
          ? _value.canRequestSync
          : canRequestSync // ignore: cast_nullable_to_non_nullable
              as bool,
    ));
  }
}

/// @nodoc

class _$SyncProfile_2StateImpl extends _SyncProfile_2State {
  const _$SyncProfile_2StateImpl(
      {required this.syncProfile, this.canRequestSync = false})
      : super._();

  @override
  final SyncProfile syncProfile;
  @override
  @JsonKey()
  final bool canRequestSync;

  @override
  String toString() {
    return 'SyncProfile_2State(syncProfile: $syncProfile, canRequestSync: $canRequestSync)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$SyncProfile_2StateImpl &&
            (identical(other.syncProfile, syncProfile) ||
                other.syncProfile == syncProfile) &&
            (identical(other.canRequestSync, canRequestSync) ||
                other.canRequestSync == canRequestSync));
  }

  @override
  int get hashCode => Object.hash(runtimeType, syncProfile, canRequestSync);

  @JsonKey(ignore: true)
  @override
  @pragma('vm:prefer-inline')
  _$$SyncProfile_2StateImplCopyWith<_$SyncProfile_2StateImpl> get copyWith =>
      __$$SyncProfile_2StateImplCopyWithImpl<_$SyncProfile_2StateImpl>(
          this, _$identity);
}

abstract class _SyncProfile_2State extends SyncProfile_2State {
  const factory _SyncProfile_2State(
      {required final SyncProfile syncProfile,
      final bool canRequestSync}) = _$SyncProfile_2StateImpl;
  const _SyncProfile_2State._() : super._();

  @override
  SyncProfile get syncProfile;
  @override
  bool get canRequestSync;
  @override
  @JsonKey(ignore: true)
  _$$SyncProfile_2StateImplCopyWith<_$SyncProfile_2StateImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
