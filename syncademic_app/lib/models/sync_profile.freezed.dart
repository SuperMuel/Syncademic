// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'sync_profile.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

/// @nodoc
mixin _$SyncProfile {
  ID get id => throw _privateConstructorUsedError;
  ScheduleSource get scheduleSource => throw _privateConstructorUsedError;
  TargetCalendar get targetCalendar => throw _privateConstructorUsedError;
  String get title => throw _privateConstructorUsedError;
  bool get enabled => throw _privateConstructorUsedError;
  SyncProfileStatus? get status => throw _privateConstructorUsedError;

  @JsonKey(ignore: true)
  $SyncProfileCopyWith<SyncProfile> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $SyncProfileCopyWith<$Res> {
  factory $SyncProfileCopyWith(
          SyncProfile value, $Res Function(SyncProfile) then) =
      _$SyncProfileCopyWithImpl<$Res, SyncProfile>;
  @useResult
  $Res call(
      {ID id,
      ScheduleSource scheduleSource,
      TargetCalendar targetCalendar,
      String title,
      bool enabled,
      SyncProfileStatus? status});

  $ScheduleSourceCopyWith<$Res> get scheduleSource;
  $TargetCalendarCopyWith<$Res> get targetCalendar;
  $SyncProfileStatusCopyWith<$Res>? get status;
}

/// @nodoc
class _$SyncProfileCopyWithImpl<$Res, $Val extends SyncProfile>
    implements $SyncProfileCopyWith<$Res> {
  _$SyncProfileCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? scheduleSource = null,
    Object? targetCalendar = null,
    Object? title = null,
    Object? enabled = null,
    Object? status = freezed,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as ID,
      scheduleSource: null == scheduleSource
          ? _value.scheduleSource
          : scheduleSource // ignore: cast_nullable_to_non_nullable
              as ScheduleSource,
      targetCalendar: null == targetCalendar
          ? _value.targetCalendar
          : targetCalendar // ignore: cast_nullable_to_non_nullable
              as TargetCalendar,
      title: null == title
          ? _value.title
          : title // ignore: cast_nullable_to_non_nullable
              as String,
      enabled: null == enabled
          ? _value.enabled
          : enabled // ignore: cast_nullable_to_non_nullable
              as bool,
      status: freezed == status
          ? _value.status
          : status // ignore: cast_nullable_to_non_nullable
              as SyncProfileStatus?,
    ) as $Val);
  }

  @override
  @pragma('vm:prefer-inline')
  $ScheduleSourceCopyWith<$Res> get scheduleSource {
    return $ScheduleSourceCopyWith<$Res>(_value.scheduleSource, (value) {
      return _then(_value.copyWith(scheduleSource: value) as $Val);
    });
  }

  @override
  @pragma('vm:prefer-inline')
  $TargetCalendarCopyWith<$Res> get targetCalendar {
    return $TargetCalendarCopyWith<$Res>(_value.targetCalendar, (value) {
      return _then(_value.copyWith(targetCalendar: value) as $Val);
    });
  }

  @override
  @pragma('vm:prefer-inline')
  $SyncProfileStatusCopyWith<$Res>? get status {
    if (_value.status == null) {
      return null;
    }

    return $SyncProfileStatusCopyWith<$Res>(_value.status!, (value) {
      return _then(_value.copyWith(status: value) as $Val);
    });
  }
}

/// @nodoc
abstract class _$$SyncProfileImplCopyWith<$Res>
    implements $SyncProfileCopyWith<$Res> {
  factory _$$SyncProfileImplCopyWith(
          _$SyncProfileImpl value, $Res Function(_$SyncProfileImpl) then) =
      __$$SyncProfileImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {ID id,
      ScheduleSource scheduleSource,
      TargetCalendar targetCalendar,
      String title,
      bool enabled,
      SyncProfileStatus? status});

  @override
  $ScheduleSourceCopyWith<$Res> get scheduleSource;
  @override
  $TargetCalendarCopyWith<$Res> get targetCalendar;
  @override
  $SyncProfileStatusCopyWith<$Res>? get status;
}

/// @nodoc
class __$$SyncProfileImplCopyWithImpl<$Res>
    extends _$SyncProfileCopyWithImpl<$Res, _$SyncProfileImpl>
    implements _$$SyncProfileImplCopyWith<$Res> {
  __$$SyncProfileImplCopyWithImpl(
      _$SyncProfileImpl _value, $Res Function(_$SyncProfileImpl) _then)
      : super(_value, _then);

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? scheduleSource = null,
    Object? targetCalendar = null,
    Object? title = null,
    Object? enabled = null,
    Object? status = freezed,
  }) {
    return _then(_$SyncProfileImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as ID,
      scheduleSource: null == scheduleSource
          ? _value.scheduleSource
          : scheduleSource // ignore: cast_nullable_to_non_nullable
              as ScheduleSource,
      targetCalendar: null == targetCalendar
          ? _value.targetCalendar
          : targetCalendar // ignore: cast_nullable_to_non_nullable
              as TargetCalendar,
      title: null == title
          ? _value.title
          : title // ignore: cast_nullable_to_non_nullable
              as String,
      enabled: null == enabled
          ? _value.enabled
          : enabled // ignore: cast_nullable_to_non_nullable
              as bool,
      status: freezed == status
          ? _value.status
          : status // ignore: cast_nullable_to_non_nullable
              as SyncProfileStatus?,
    ));
  }
}

/// @nodoc

class _$SyncProfileImpl implements _SyncProfile {
  const _$SyncProfileImpl(
      {required this.id,
      required this.scheduleSource,
      required this.targetCalendar,
      required this.title,
      this.enabled = false,
      this.status});

  @override
  final ID id;
  @override
  final ScheduleSource scheduleSource;
  @override
  final TargetCalendar targetCalendar;
  @override
  final String title;
  @override
  @JsonKey()
  final bool enabled;
  @override
  final SyncProfileStatus? status;

  @override
  String toString() {
    return 'SyncProfile(id: $id, scheduleSource: $scheduleSource, targetCalendar: $targetCalendar, title: $title, enabled: $enabled, status: $status)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$SyncProfileImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.scheduleSource, scheduleSource) ||
                other.scheduleSource == scheduleSource) &&
            (identical(other.targetCalendar, targetCalendar) ||
                other.targetCalendar == targetCalendar) &&
            (identical(other.title, title) || other.title == title) &&
            (identical(other.enabled, enabled) || other.enabled == enabled) &&
            (identical(other.status, status) || other.status == status));
  }

  @override
  int get hashCode => Object.hash(
      runtimeType, id, scheduleSource, targetCalendar, title, enabled, status);

  @JsonKey(ignore: true)
  @override
  @pragma('vm:prefer-inline')
  _$$SyncProfileImplCopyWith<_$SyncProfileImpl> get copyWith =>
      __$$SyncProfileImplCopyWithImpl<_$SyncProfileImpl>(this, _$identity);
}

abstract class _SyncProfile implements SyncProfile {
  const factory _SyncProfile(
      {required final ID id,
      required final ScheduleSource scheduleSource,
      required final TargetCalendar targetCalendar,
      required final String title,
      final bool enabled,
      final SyncProfileStatus? status}) = _$SyncProfileImpl;

  @override
  ID get id;
  @override
  ScheduleSource get scheduleSource;
  @override
  TargetCalendar get targetCalendar;
  @override
  String get title;
  @override
  bool get enabled;
  @override
  SyncProfileStatus? get status;
  @override
  @JsonKey(ignore: true)
  _$$SyncProfileImplCopyWith<_$SyncProfileImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
