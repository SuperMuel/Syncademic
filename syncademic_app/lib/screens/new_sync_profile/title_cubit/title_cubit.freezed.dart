// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'title_cubit.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

/// @nodoc
mixin _$TitleState {
  String get title => throw _privateConstructorUsedError;
  String? get error => throw _privateConstructorUsedError;

  @JsonKey(ignore: true)
  $TitleStateCopyWith<TitleState> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $TitleStateCopyWith<$Res> {
  factory $TitleStateCopyWith(
          TitleState value, $Res Function(TitleState) then) =
      _$TitleStateCopyWithImpl<$Res, TitleState>;
  @useResult
  $Res call({String title, String? error});
}

/// @nodoc
class _$TitleStateCopyWithImpl<$Res, $Val extends TitleState>
    implements $TitleStateCopyWith<$Res> {
  _$TitleStateCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? title = null,
    Object? error = freezed,
  }) {
    return _then(_value.copyWith(
      title: null == title
          ? _value.title
          : title // ignore: cast_nullable_to_non_nullable
              as String,
      error: freezed == error
          ? _value.error
          : error // ignore: cast_nullable_to_non_nullable
              as String?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$TitleStateImplCopyWith<$Res>
    implements $TitleStateCopyWith<$Res> {
  factory _$$TitleStateImplCopyWith(
          _$TitleStateImpl value, $Res Function(_$TitleStateImpl) then) =
      __$$TitleStateImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({String title, String? error});
}

/// @nodoc
class __$$TitleStateImplCopyWithImpl<$Res>
    extends _$TitleStateCopyWithImpl<$Res, _$TitleStateImpl>
    implements _$$TitleStateImplCopyWith<$Res> {
  __$$TitleStateImplCopyWithImpl(
      _$TitleStateImpl _value, $Res Function(_$TitleStateImpl) _then)
      : super(_value, _then);

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? title = null,
    Object? error = freezed,
  }) {
    return _then(_$TitleStateImpl(
      title: null == title
          ? _value.title
          : title // ignore: cast_nullable_to_non_nullable
              as String,
      error: freezed == error
          ? _value.error
          : error // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc

class _$TitleStateImpl extends _TitleState {
  const _$TitleStateImpl({this.title = "", this.error}) : super._();

  @override
  @JsonKey()
  final String title;
  @override
  final String? error;

  @override
  String toString() {
    return 'TitleState(title: $title, error: $error)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$TitleStateImpl &&
            (identical(other.title, title) || other.title == title) &&
            (identical(other.error, error) || other.error == error));
  }

  @override
  int get hashCode => Object.hash(runtimeType, title, error);

  @JsonKey(ignore: true)
  @override
  @pragma('vm:prefer-inline')
  _$$TitleStateImplCopyWith<_$TitleStateImpl> get copyWith =>
      __$$TitleStateImplCopyWithImpl<_$TitleStateImpl>(this, _$identity);
}

abstract class _TitleState extends TitleState {
  const factory _TitleState({final String title, final String? error}) =
      _$TitleStateImpl;
  const _TitleState._() : super._();

  @override
  String get title;
  @override
  String? get error;
  @override
  @JsonKey(ignore: true)
  _$$TitleStateImplCopyWith<_$TitleStateImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
