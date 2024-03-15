// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'schedule_source.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

/// @nodoc
mixin _$ScheduleSource {
  String get url => throw _privateConstructorUsedError;

  @JsonKey(ignore: true)
  $ScheduleSourceCopyWith<ScheduleSource> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ScheduleSourceCopyWith<$Res> {
  factory $ScheduleSourceCopyWith(
          ScheduleSource value, $Res Function(ScheduleSource) then) =
      _$ScheduleSourceCopyWithImpl<$Res, ScheduleSource>;
  @useResult
  $Res call({String url});
}

/// @nodoc
class _$ScheduleSourceCopyWithImpl<$Res, $Val extends ScheduleSource>
    implements $ScheduleSourceCopyWith<$Res> {
  _$ScheduleSourceCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? url = null,
  }) {
    return _then(_value.copyWith(
      url: null == url
          ? _value.url
          : url // ignore: cast_nullable_to_non_nullable
              as String,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$ScheduleSourceImplCopyWith<$Res>
    implements $ScheduleSourceCopyWith<$Res> {
  factory _$$ScheduleSourceImplCopyWith(_$ScheduleSourceImpl value,
          $Res Function(_$ScheduleSourceImpl) then) =
      __$$ScheduleSourceImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({String url});
}

/// @nodoc
class __$$ScheduleSourceImplCopyWithImpl<$Res>
    extends _$ScheduleSourceCopyWithImpl<$Res, _$ScheduleSourceImpl>
    implements _$$ScheduleSourceImplCopyWith<$Res> {
  __$$ScheduleSourceImplCopyWithImpl(
      _$ScheduleSourceImpl _value, $Res Function(_$ScheduleSourceImpl) _then)
      : super(_value, _then);

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? url = null,
  }) {
    return _then(_$ScheduleSourceImpl(
      url: null == url
          ? _value.url
          : url // ignore: cast_nullable_to_non_nullable
              as String,
    ));
  }
}

/// @nodoc

class _$ScheduleSourceImpl implements _ScheduleSource {
  const _$ScheduleSourceImpl({required this.url});

  @override
  final String url;

  @override
  String toString() {
    return 'ScheduleSource(url: $url)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ScheduleSourceImpl &&
            (identical(other.url, url) || other.url == url));
  }

  @override
  int get hashCode => Object.hash(runtimeType, url);

  @JsonKey(ignore: true)
  @override
  @pragma('vm:prefer-inline')
  _$$ScheduleSourceImplCopyWith<_$ScheduleSourceImpl> get copyWith =>
      __$$ScheduleSourceImplCopyWithImpl<_$ScheduleSourceImpl>(
          this, _$identity);
}

abstract class _ScheduleSource implements ScheduleSource {
  const factory _ScheduleSource({required final String url}) =
      _$ScheduleSourceImpl;

  @override
  String get url;
  @override
  @JsonKey(ignore: true)
  _$$ScheduleSourceImplCopyWith<_$ScheduleSourceImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
