// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'target_calendar_selector_cubit.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

/// @nodoc
mixin _$TargetCalendarSelectorState {
  dynamic get loading => throw _privateConstructorUsedError;
  String? get error => throw _privateConstructorUsedError;
  List<TargetCalendar> get calendars => throw _privateConstructorUsedError;
  TargetCalendar? get selected => throw _privateConstructorUsedError;

  @JsonKey(ignore: true)
  $TargetCalendarSelectorStateCopyWith<TargetCalendarSelectorState>
      get copyWith => throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $TargetCalendarSelectorStateCopyWith<$Res> {
  factory $TargetCalendarSelectorStateCopyWith(
          TargetCalendarSelectorState value,
          $Res Function(TargetCalendarSelectorState) then) =
      _$TargetCalendarSelectorStateCopyWithImpl<$Res,
          TargetCalendarSelectorState>;
  @useResult
  $Res call(
      {dynamic loading,
      String? error,
      List<TargetCalendar> calendars,
      TargetCalendar? selected});

  $TargetCalendarCopyWith<$Res>? get selected;
}

/// @nodoc
class _$TargetCalendarSelectorStateCopyWithImpl<$Res,
        $Val extends TargetCalendarSelectorState>
    implements $TargetCalendarSelectorStateCopyWith<$Res> {
  _$TargetCalendarSelectorStateCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? loading = freezed,
    Object? error = freezed,
    Object? calendars = null,
    Object? selected = freezed,
  }) {
    return _then(_value.copyWith(
      loading: freezed == loading
          ? _value.loading
          : loading // ignore: cast_nullable_to_non_nullable
              as dynamic,
      error: freezed == error
          ? _value.error
          : error // ignore: cast_nullable_to_non_nullable
              as String?,
      calendars: null == calendars
          ? _value.calendars
          : calendars // ignore: cast_nullable_to_non_nullable
              as List<TargetCalendar>,
      selected: freezed == selected
          ? _value.selected
          : selected // ignore: cast_nullable_to_non_nullable
              as TargetCalendar?,
    ) as $Val);
  }

  @override
  @pragma('vm:prefer-inline')
  $TargetCalendarCopyWith<$Res>? get selected {
    if (_value.selected == null) {
      return null;
    }

    return $TargetCalendarCopyWith<$Res>(_value.selected!, (value) {
      return _then(_value.copyWith(selected: value) as $Val);
    });
  }
}

/// @nodoc
abstract class _$$TargetCalendarSelectorStateImplCopyWith<$Res>
    implements $TargetCalendarSelectorStateCopyWith<$Res> {
  factory _$$TargetCalendarSelectorStateImplCopyWith(
          _$TargetCalendarSelectorStateImpl value,
          $Res Function(_$TargetCalendarSelectorStateImpl) then) =
      __$$TargetCalendarSelectorStateImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {dynamic loading,
      String? error,
      List<TargetCalendar> calendars,
      TargetCalendar? selected});

  @override
  $TargetCalendarCopyWith<$Res>? get selected;
}

/// @nodoc
class __$$TargetCalendarSelectorStateImplCopyWithImpl<$Res>
    extends _$TargetCalendarSelectorStateCopyWithImpl<$Res,
        _$TargetCalendarSelectorStateImpl>
    implements _$$TargetCalendarSelectorStateImplCopyWith<$Res> {
  __$$TargetCalendarSelectorStateImplCopyWithImpl(
      _$TargetCalendarSelectorStateImpl _value,
      $Res Function(_$TargetCalendarSelectorStateImpl) _then)
      : super(_value, _then);

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? loading = freezed,
    Object? error = freezed,
    Object? calendars = null,
    Object? selected = freezed,
  }) {
    return _then(_$TargetCalendarSelectorStateImpl(
      loading: freezed == loading ? _value.loading! : loading,
      error: freezed == error
          ? _value.error
          : error // ignore: cast_nullable_to_non_nullable
              as String?,
      calendars: null == calendars
          ? _value._calendars
          : calendars // ignore: cast_nullable_to_non_nullable
              as List<TargetCalendar>,
      selected: freezed == selected
          ? _value.selected
          : selected // ignore: cast_nullable_to_non_nullable
              as TargetCalendar?,
    ));
  }
}

/// @nodoc

class _$TargetCalendarSelectorStateImpl
    implements _TargetCalendarSelectorState {
  const _$TargetCalendarSelectorStateImpl(
      {this.loading = true,
      this.error,
      final List<TargetCalendar> calendars = const [],
      this.selected})
      : _calendars = calendars;

  @override
  @JsonKey()
  final dynamic loading;
  @override
  final String? error;
  final List<TargetCalendar> _calendars;
  @override
  @JsonKey()
  List<TargetCalendar> get calendars {
    if (_calendars is EqualUnmodifiableListView) return _calendars;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_calendars);
  }

  @override
  final TargetCalendar? selected;

  @override
  String toString() {
    return 'TargetCalendarSelectorState(loading: $loading, error: $error, calendars: $calendars, selected: $selected)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$TargetCalendarSelectorStateImpl &&
            const DeepCollectionEquality().equals(other.loading, loading) &&
            (identical(other.error, error) || other.error == error) &&
            const DeepCollectionEquality()
                .equals(other._calendars, _calendars) &&
            (identical(other.selected, selected) ||
                other.selected == selected));
  }

  @override
  int get hashCode => Object.hash(
      runtimeType,
      const DeepCollectionEquality().hash(loading),
      error,
      const DeepCollectionEquality().hash(_calendars),
      selected);

  @JsonKey(ignore: true)
  @override
  @pragma('vm:prefer-inline')
  _$$TargetCalendarSelectorStateImplCopyWith<_$TargetCalendarSelectorStateImpl>
      get copyWith => __$$TargetCalendarSelectorStateImplCopyWithImpl<
          _$TargetCalendarSelectorStateImpl>(this, _$identity);
}

abstract class _TargetCalendarSelectorState
    implements TargetCalendarSelectorState {
  const factory _TargetCalendarSelectorState(
      {final dynamic loading,
      final String? error,
      final List<TargetCalendar> calendars,
      final TargetCalendar? selected}) = _$TargetCalendarSelectorStateImpl;

  @override
  dynamic get loading;
  @override
  String? get error;
  @override
  List<TargetCalendar> get calendars;
  @override
  TargetCalendar? get selected;
  @override
  @JsonKey(ignore: true)
  _$$TargetCalendarSelectorStateImplCopyWith<_$TargetCalendarSelectorStateImpl>
      get copyWith => throw _privateConstructorUsedError;
}
