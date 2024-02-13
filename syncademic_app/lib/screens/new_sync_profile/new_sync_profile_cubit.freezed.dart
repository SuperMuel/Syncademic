// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'new_sync_profile_cubit.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

/// @nodoc
mixin _$NewSyncProfileState {
  String get url => throw _privateConstructorUsedError;
  String? get urlError => throw _privateConstructorUsedError;
  bool get isSubmitting => throw _privateConstructorUsedError;

  @JsonKey(ignore: true)
  $NewSyncProfileStateCopyWith<NewSyncProfileState> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $NewSyncProfileStateCopyWith<$Res> {
  factory $NewSyncProfileStateCopyWith(
          NewSyncProfileState value, $Res Function(NewSyncProfileState) then) =
      _$NewSyncProfileStateCopyWithImpl<$Res, NewSyncProfileState>;
  @useResult
  $Res call({String url, String? urlError, bool isSubmitting});
}

/// @nodoc
class _$NewSyncProfileStateCopyWithImpl<$Res, $Val extends NewSyncProfileState>
    implements $NewSyncProfileStateCopyWith<$Res> {
  _$NewSyncProfileStateCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? url = null,
    Object? urlError = freezed,
    Object? isSubmitting = null,
  }) {
    return _then(_value.copyWith(
      url: null == url
          ? _value.url
          : url // ignore: cast_nullable_to_non_nullable
              as String,
      urlError: freezed == urlError
          ? _value.urlError
          : urlError // ignore: cast_nullable_to_non_nullable
              as String?,
      isSubmitting: null == isSubmitting
          ? _value.isSubmitting
          : isSubmitting // ignore: cast_nullable_to_non_nullable
              as bool,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$NewSyncProfileStateImplCopyWith<$Res>
    implements $NewSyncProfileStateCopyWith<$Res> {
  factory _$$NewSyncProfileStateImplCopyWith(_$NewSyncProfileStateImpl value,
          $Res Function(_$NewSyncProfileStateImpl) then) =
      __$$NewSyncProfileStateImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({String url, String? urlError, bool isSubmitting});
}

/// @nodoc
class __$$NewSyncProfileStateImplCopyWithImpl<$Res>
    extends _$NewSyncProfileStateCopyWithImpl<$Res, _$NewSyncProfileStateImpl>
    implements _$$NewSyncProfileStateImplCopyWith<$Res> {
  __$$NewSyncProfileStateImplCopyWithImpl(_$NewSyncProfileStateImpl _value,
      $Res Function(_$NewSyncProfileStateImpl) _then)
      : super(_value, _then);

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? url = null,
    Object? urlError = freezed,
    Object? isSubmitting = null,
  }) {
    return _then(_$NewSyncProfileStateImpl(
      url: null == url
          ? _value.url
          : url // ignore: cast_nullable_to_non_nullable
              as String,
      urlError: freezed == urlError
          ? _value.urlError
          : urlError // ignore: cast_nullable_to_non_nullable
              as String?,
      isSubmitting: null == isSubmitting
          ? _value.isSubmitting
          : isSubmitting // ignore: cast_nullable_to_non_nullable
              as bool,
    ));
  }
}

/// @nodoc

class _$NewSyncProfileStateImpl extends _NewSyncProfileState {
  const _$NewSyncProfileStateImpl(
      {this.url = '', this.urlError = null, this.isSubmitting = false})
      : super._();

  @override
  @JsonKey()
  final String url;
  @override
  @JsonKey()
  final String? urlError;
  @override
  @JsonKey()
  final bool isSubmitting;

  @override
  String toString() {
    return 'NewSyncProfileState(url: $url, urlError: $urlError, isSubmitting: $isSubmitting)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$NewSyncProfileStateImpl &&
            (identical(other.url, url) || other.url == url) &&
            (identical(other.urlError, urlError) ||
                other.urlError == urlError) &&
            (identical(other.isSubmitting, isSubmitting) ||
                other.isSubmitting == isSubmitting));
  }

  @override
  int get hashCode => Object.hash(runtimeType, url, urlError, isSubmitting);

  @JsonKey(ignore: true)
  @override
  @pragma('vm:prefer-inline')
  _$$NewSyncProfileStateImplCopyWith<_$NewSyncProfileStateImpl> get copyWith =>
      __$$NewSyncProfileStateImplCopyWithImpl<_$NewSyncProfileStateImpl>(
          this, _$identity);
}

abstract class _NewSyncProfileState extends NewSyncProfileState {
  const factory _NewSyncProfileState(
      {final String url,
      final String? urlError,
      final bool isSubmitting}) = _$NewSyncProfileStateImpl;
  const _NewSyncProfileState._() : super._();

  @override
  String get url;
  @override
  String? get urlError;
  @override
  bool get isSubmitting;
  @override
  @JsonKey(ignore: true)
  _$$NewSyncProfileStateImplCopyWith<_$NewSyncProfileStateImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
