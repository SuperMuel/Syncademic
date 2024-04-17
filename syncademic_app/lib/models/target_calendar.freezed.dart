// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'target_calendar.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

/// @nodoc
mixin _$TargetCalendar {
  /// The unique identifier for the calendar.
  ///
  /// For Google Calendar, this is the ID of the calendar provided by Google.
  ID get id => throw _privateConstructorUsedError;

  /// The title of the calendar, as provided by the calendar service.
  String get title => throw _privateConstructorUsedError;

  /// The unique identifier for the user account that owns the calendar.
  ///
  /// This identifier represents the specific user account associated with the calendar,
  /// and it varies depending on the calendar service being used.
  ///
  /// For Google Calendar:
  /// - The `accountOwnerUserId` is the ID of the Google Account that owns the calendar.
  ///
  /// For Microsoft Outlook:
  /// - The `accountOwnerUserId` is the ID of the Microsoft Outlook account that owns the calendar.
  ///
  /// Note: The `accountOwnerUserId` is different from the `id` property, which represents the unique identifier
  /// of the calendar itself. It is also different from the user ID that is logged in to the Syncademic app,
  /// as a user can have multiple accounts on multiple calendar services.
  String get accountOwnerUserId => throw _privateConstructorUsedError;
  bool? get createdBySyncademic => throw _privateConstructorUsedError;

  @JsonKey(ignore: true)
  $TargetCalendarCopyWith<TargetCalendar> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $TargetCalendarCopyWith<$Res> {
  factory $TargetCalendarCopyWith(
          TargetCalendar value, $Res Function(TargetCalendar) then) =
      _$TargetCalendarCopyWithImpl<$Res, TargetCalendar>;
  @useResult
  $Res call(
      {ID id,
      String title,
      String accountOwnerUserId,
      bool? createdBySyncademic});
}

/// @nodoc
class _$TargetCalendarCopyWithImpl<$Res, $Val extends TargetCalendar>
    implements $TargetCalendarCopyWith<$Res> {
  _$TargetCalendarCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? title = null,
    Object? accountOwnerUserId = null,
    Object? createdBySyncademic = freezed,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as ID,
      title: null == title
          ? _value.title
          : title // ignore: cast_nullable_to_non_nullable
              as String,
      accountOwnerUserId: null == accountOwnerUserId
          ? _value.accountOwnerUserId
          : accountOwnerUserId // ignore: cast_nullable_to_non_nullable
              as String,
      createdBySyncademic: freezed == createdBySyncademic
          ? _value.createdBySyncademic
          : createdBySyncademic // ignore: cast_nullable_to_non_nullable
              as bool?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$TargetCalendarImplCopyWith<$Res>
    implements $TargetCalendarCopyWith<$Res> {
  factory _$$TargetCalendarImplCopyWith(_$TargetCalendarImpl value,
          $Res Function(_$TargetCalendarImpl) then) =
      __$$TargetCalendarImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {ID id,
      String title,
      String accountOwnerUserId,
      bool? createdBySyncademic});
}

/// @nodoc
class __$$TargetCalendarImplCopyWithImpl<$Res>
    extends _$TargetCalendarCopyWithImpl<$Res, _$TargetCalendarImpl>
    implements _$$TargetCalendarImplCopyWith<$Res> {
  __$$TargetCalendarImplCopyWithImpl(
      _$TargetCalendarImpl _value, $Res Function(_$TargetCalendarImpl) _then)
      : super(_value, _then);

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? title = null,
    Object? accountOwnerUserId = null,
    Object? createdBySyncademic = freezed,
  }) {
    return _then(_$TargetCalendarImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as ID,
      title: null == title
          ? _value.title
          : title // ignore: cast_nullable_to_non_nullable
              as String,
      accountOwnerUserId: null == accountOwnerUserId
          ? _value.accountOwnerUserId
          : accountOwnerUserId // ignore: cast_nullable_to_non_nullable
              as String,
      createdBySyncademic: freezed == createdBySyncademic
          ? _value.createdBySyncademic
          : createdBySyncademic // ignore: cast_nullable_to_non_nullable
              as bool?,
    ));
  }
}

/// @nodoc

class _$TargetCalendarImpl implements _TargetCalendar {
  const _$TargetCalendarImpl(
      {required this.id,
      required this.title,
      required this.accountOwnerUserId,
      this.createdBySyncademic});

  /// The unique identifier for the calendar.
  ///
  /// For Google Calendar, this is the ID of the calendar provided by Google.
  @override
  final ID id;

  /// The title of the calendar, as provided by the calendar service.
  @override
  final String title;

  /// The unique identifier for the user account that owns the calendar.
  ///
  /// This identifier represents the specific user account associated with the calendar,
  /// and it varies depending on the calendar service being used.
  ///
  /// For Google Calendar:
  /// - The `accountOwnerUserId` is the ID of the Google Account that owns the calendar.
  ///
  /// For Microsoft Outlook:
  /// - The `accountOwnerUserId` is the ID of the Microsoft Outlook account that owns the calendar.
  ///
  /// Note: The `accountOwnerUserId` is different from the `id` property, which represents the unique identifier
  /// of the calendar itself. It is also different from the user ID that is logged in to the Syncademic app,
  /// as a user can have multiple accounts on multiple calendar services.
  @override
  final String accountOwnerUserId;
  @override
  final bool? createdBySyncademic;

  @override
  String toString() {
    return 'TargetCalendar(id: $id, title: $title, accountOwnerUserId: $accountOwnerUserId, createdBySyncademic: $createdBySyncademic)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$TargetCalendarImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.title, title) || other.title == title) &&
            (identical(other.accountOwnerUserId, accountOwnerUserId) ||
                other.accountOwnerUserId == accountOwnerUserId) &&
            (identical(other.createdBySyncademic, createdBySyncademic) ||
                other.createdBySyncademic == createdBySyncademic));
  }

  @override
  int get hashCode => Object.hash(
      runtimeType, id, title, accountOwnerUserId, createdBySyncademic);

  @JsonKey(ignore: true)
  @override
  @pragma('vm:prefer-inline')
  _$$TargetCalendarImplCopyWith<_$TargetCalendarImpl> get copyWith =>
      __$$TargetCalendarImplCopyWithImpl<_$TargetCalendarImpl>(
          this, _$identity);
}

abstract class _TargetCalendar implements TargetCalendar {
  const factory _TargetCalendar(
      {required final ID id,
      required final String title,
      required final String accountOwnerUserId,
      final bool? createdBySyncademic}) = _$TargetCalendarImpl;

  @override

  /// The unique identifier for the calendar.
  ///
  /// For Google Calendar, this is the ID of the calendar provided by Google.
  ID get id;
  @override

  /// The title of the calendar, as provided by the calendar service.
  String get title;
  @override

  /// The unique identifier for the user account that owns the calendar.
  ///
  /// This identifier represents the specific user account associated with the calendar,
  /// and it varies depending on the calendar service being used.
  ///
  /// For Google Calendar:
  /// - The `accountOwnerUserId` is the ID of the Google Account that owns the calendar.
  ///
  /// For Microsoft Outlook:
  /// - The `accountOwnerUserId` is the ID of the Microsoft Outlook account that owns the calendar.
  ///
  /// Note: The `accountOwnerUserId` is different from the `id` property, which represents the unique identifier
  /// of the calendar itself. It is also different from the user ID that is logged in to the Syncademic app,
  /// as a user can have multiple accounts on multiple calendar services.
  String get accountOwnerUserId;
  @override
  bool? get createdBySyncademic;
  @override
  @JsonKey(ignore: true)
  _$$TargetCalendarImplCopyWith<_$TargetCalendarImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
