// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'stepper_cubit.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

/// @nodoc
mixin _$StepperState {
  int get currentStep => throw _privateConstructorUsedError;
  String get title => throw _privateConstructorUsedError;
  String? get titleError => throw _privateConstructorUsedError;
  String get url => throw _privateConstructorUsedError;
  String? get urlError => throw _privateConstructorUsedError;
  TargetCalendar? get targetCalendar => throw _privateConstructorUsedError;
  String? get backendAuthorization => throw _privateConstructorUsedError;

  @JsonKey(ignore: true)
  $StepperStateCopyWith<StepperState> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $StepperStateCopyWith<$Res> {
  factory $StepperStateCopyWith(
          StepperState value, $Res Function(StepperState) then) =
      _$StepperStateCopyWithImpl<$Res, StepperState>;
  @useResult
  $Res call(
      {int currentStep,
      String title,
      String? titleError,
      String url,
      String? urlError,
      TargetCalendar? targetCalendar,
      String? backendAuthorization});

  $TargetCalendarCopyWith<$Res>? get targetCalendar;
}

/// @nodoc
class _$StepperStateCopyWithImpl<$Res, $Val extends StepperState>
    implements $StepperStateCopyWith<$Res> {
  _$StepperStateCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? currentStep = null,
    Object? title = null,
    Object? titleError = freezed,
    Object? url = null,
    Object? urlError = freezed,
    Object? targetCalendar = freezed,
    Object? backendAuthorization = freezed,
  }) {
    return _then(_value.copyWith(
      currentStep: null == currentStep
          ? _value.currentStep
          : currentStep // ignore: cast_nullable_to_non_nullable
              as int,
      title: null == title
          ? _value.title
          : title // ignore: cast_nullable_to_non_nullable
              as String,
      titleError: freezed == titleError
          ? _value.titleError
          : titleError // ignore: cast_nullable_to_non_nullable
              as String?,
      url: null == url
          ? _value.url
          : url // ignore: cast_nullable_to_non_nullable
              as String,
      urlError: freezed == urlError
          ? _value.urlError
          : urlError // ignore: cast_nullable_to_non_nullable
              as String?,
      targetCalendar: freezed == targetCalendar
          ? _value.targetCalendar
          : targetCalendar // ignore: cast_nullable_to_non_nullable
              as TargetCalendar?,
      backendAuthorization: freezed == backendAuthorization
          ? _value.backendAuthorization
          : backendAuthorization // ignore: cast_nullable_to_non_nullable
              as String?,
    ) as $Val);
  }

  @override
  @pragma('vm:prefer-inline')
  $TargetCalendarCopyWith<$Res>? get targetCalendar {
    if (_value.targetCalendar == null) {
      return null;
    }

    return $TargetCalendarCopyWith<$Res>(_value.targetCalendar!, (value) {
      return _then(_value.copyWith(targetCalendar: value) as $Val);
    });
  }
}

/// @nodoc
abstract class _$$StepperStateImplCopyWith<$Res>
    implements $StepperStateCopyWith<$Res> {
  factory _$$StepperStateImplCopyWith(
          _$StepperStateImpl value, $Res Function(_$StepperStateImpl) then) =
      __$$StepperStateImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {int currentStep,
      String title,
      String? titleError,
      String url,
      String? urlError,
      TargetCalendar? targetCalendar,
      String? backendAuthorization});

  @override
  $TargetCalendarCopyWith<$Res>? get targetCalendar;
}

/// @nodoc
class __$$StepperStateImplCopyWithImpl<$Res>
    extends _$StepperStateCopyWithImpl<$Res, _$StepperStateImpl>
    implements _$$StepperStateImplCopyWith<$Res> {
  __$$StepperStateImplCopyWithImpl(
      _$StepperStateImpl _value, $Res Function(_$StepperStateImpl) _then)
      : super(_value, _then);

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? currentStep = null,
    Object? title = null,
    Object? titleError = freezed,
    Object? url = null,
    Object? urlError = freezed,
    Object? targetCalendar = freezed,
    Object? backendAuthorization = freezed,
  }) {
    return _then(_$StepperStateImpl(
      currentStep: null == currentStep
          ? _value.currentStep
          : currentStep // ignore: cast_nullable_to_non_nullable
              as int,
      title: null == title
          ? _value.title
          : title // ignore: cast_nullable_to_non_nullable
              as String,
      titleError: freezed == titleError
          ? _value.titleError
          : titleError // ignore: cast_nullable_to_non_nullable
              as String?,
      url: null == url
          ? _value.url
          : url // ignore: cast_nullable_to_non_nullable
              as String,
      urlError: freezed == urlError
          ? _value.urlError
          : urlError // ignore: cast_nullable_to_non_nullable
              as String?,
      targetCalendar: freezed == targetCalendar
          ? _value.targetCalendar
          : targetCalendar // ignore: cast_nullable_to_non_nullable
              as TargetCalendar?,
      backendAuthorization: freezed == backendAuthorization
          ? _value.backendAuthorization
          : backendAuthorization // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc

class _$StepperStateImpl extends _StepperState {
  const _$StepperStateImpl(
      {this.currentStep = 0,
      this.title = '',
      this.titleError,
      this.url = '',
      this.urlError,
      this.targetCalendar = null,
      this.backendAuthorization = null})
      : super._();

  @override
  @JsonKey()
  final int currentStep;
  @override
  @JsonKey()
  final String title;
  @override
  final String? titleError;
  @override
  @JsonKey()
  final String url;
  @override
  final String? urlError;
  @override
  @JsonKey()
  final TargetCalendar? targetCalendar;
  @override
  @JsonKey()
  final String? backendAuthorization;

  @override
  String toString() {
    return 'StepperState(currentStep: $currentStep, title: $title, titleError: $titleError, url: $url, urlError: $urlError, targetCalendar: $targetCalendar, backendAuthorization: $backendAuthorization)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$StepperStateImpl &&
            (identical(other.currentStep, currentStep) ||
                other.currentStep == currentStep) &&
            (identical(other.title, title) || other.title == title) &&
            (identical(other.titleError, titleError) ||
                other.titleError == titleError) &&
            (identical(other.url, url) || other.url == url) &&
            (identical(other.urlError, urlError) ||
                other.urlError == urlError) &&
            (identical(other.targetCalendar, targetCalendar) ||
                other.targetCalendar == targetCalendar) &&
            (identical(other.backendAuthorization, backendAuthorization) ||
                other.backendAuthorization == backendAuthorization));
  }

  @override
  int get hashCode => Object.hash(runtimeType, currentStep, title, titleError,
      url, urlError, targetCalendar, backendAuthorization);

  @JsonKey(ignore: true)
  @override
  @pragma('vm:prefer-inline')
  _$$StepperStateImplCopyWith<_$StepperStateImpl> get copyWith =>
      __$$StepperStateImplCopyWithImpl<_$StepperStateImpl>(this, _$identity);
}

abstract class _StepperState extends StepperState {
  const factory _StepperState(
      {final int currentStep,
      final String title,
      final String? titleError,
      final String url,
      final String? urlError,
      final TargetCalendar? targetCalendar,
      final String? backendAuthorization}) = _$StepperStateImpl;
  const _StepperState._() : super._();

  @override
  int get currentStep;
  @override
  String get title;
  @override
  String? get titleError;
  @override
  String get url;
  @override
  String? get urlError;
  @override
  TargetCalendar? get targetCalendar;
  @override
  String? get backendAuthorization;
  @override
  @JsonKey(ignore: true)
  _$$StepperStateImplCopyWith<_$StepperStateImpl> get copyWith =>
      throw _privateConstructorUsedError;
}