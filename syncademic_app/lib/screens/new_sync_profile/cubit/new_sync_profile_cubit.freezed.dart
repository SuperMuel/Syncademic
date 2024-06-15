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
  NewSyncProfileStep get currentStep => throw _privateConstructorUsedError;
  String get title => throw _privateConstructorUsedError;
  String? get titleError => throw _privateConstructorUsedError;
  String get url => throw _privateConstructorUsedError;
  String? get urlError => throw _privateConstructorUsedError;
  ProviderAccount? get providerAccount => throw _privateConstructorUsedError;
  String? get providerAccountError => throw _privateConstructorUsedError;
  TargetCalendar? get existingCalendarSelected =>
      throw _privateConstructorUsedError;
  TargetCalendar? get newCalendarCreated => throw _privateConstructorUsedError;
  BackendAuthorizationStatus get backendAuthorizationStatus =>
      throw _privateConstructorUsedError;
  String? get backendAuthorizationError => throw _privateConstructorUsedError;
  TargetCalendarChoice get targetCalendarChoice =>
      throw _privateConstructorUsedError;
  bool get isSubmitting => throw _privateConstructorUsedError;
  String? get submitError => throw _privateConstructorUsedError;
  bool get submittedSuccessfully => throw _privateConstructorUsedError;

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
  $Res call(
      {NewSyncProfileStep currentStep,
      String title,
      String? titleError,
      String url,
      String? urlError,
      ProviderAccount? providerAccount,
      String? providerAccountError,
      TargetCalendar? existingCalendarSelected,
      TargetCalendar? newCalendarCreated,
      BackendAuthorizationStatus backendAuthorizationStatus,
      String? backendAuthorizationError,
      TargetCalendarChoice targetCalendarChoice,
      bool isSubmitting,
      String? submitError,
      bool submittedSuccessfully});

  $ProviderAccountCopyWith<$Res>? get providerAccount;
  $TargetCalendarCopyWith<$Res>? get existingCalendarSelected;
  $TargetCalendarCopyWith<$Res>? get newCalendarCreated;
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
    Object? currentStep = null,
    Object? title = null,
    Object? titleError = freezed,
    Object? url = null,
    Object? urlError = freezed,
    Object? providerAccount = freezed,
    Object? providerAccountError = freezed,
    Object? existingCalendarSelected = freezed,
    Object? newCalendarCreated = freezed,
    Object? backendAuthorizationStatus = null,
    Object? backendAuthorizationError = freezed,
    Object? targetCalendarChoice = null,
    Object? isSubmitting = null,
    Object? submitError = freezed,
    Object? submittedSuccessfully = null,
  }) {
    return _then(_value.copyWith(
      currentStep: null == currentStep
          ? _value.currentStep
          : currentStep // ignore: cast_nullable_to_non_nullable
              as NewSyncProfileStep,
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
      providerAccount: freezed == providerAccount
          ? _value.providerAccount
          : providerAccount // ignore: cast_nullable_to_non_nullable
              as ProviderAccount?,
      providerAccountError: freezed == providerAccountError
          ? _value.providerAccountError
          : providerAccountError // ignore: cast_nullable_to_non_nullable
              as String?,
      existingCalendarSelected: freezed == existingCalendarSelected
          ? _value.existingCalendarSelected
          : existingCalendarSelected // ignore: cast_nullable_to_non_nullable
              as TargetCalendar?,
      newCalendarCreated: freezed == newCalendarCreated
          ? _value.newCalendarCreated
          : newCalendarCreated // ignore: cast_nullable_to_non_nullable
              as TargetCalendar?,
      backendAuthorizationStatus: null == backendAuthorizationStatus
          ? _value.backendAuthorizationStatus
          : backendAuthorizationStatus // ignore: cast_nullable_to_non_nullable
              as BackendAuthorizationStatus,
      backendAuthorizationError: freezed == backendAuthorizationError
          ? _value.backendAuthorizationError
          : backendAuthorizationError // ignore: cast_nullable_to_non_nullable
              as String?,
      targetCalendarChoice: null == targetCalendarChoice
          ? _value.targetCalendarChoice
          : targetCalendarChoice // ignore: cast_nullable_to_non_nullable
              as TargetCalendarChoice,
      isSubmitting: null == isSubmitting
          ? _value.isSubmitting
          : isSubmitting // ignore: cast_nullable_to_non_nullable
              as bool,
      submitError: freezed == submitError
          ? _value.submitError
          : submitError // ignore: cast_nullable_to_non_nullable
              as String?,
      submittedSuccessfully: null == submittedSuccessfully
          ? _value.submittedSuccessfully
          : submittedSuccessfully // ignore: cast_nullable_to_non_nullable
              as bool,
    ) as $Val);
  }

  @override
  @pragma('vm:prefer-inline')
  $ProviderAccountCopyWith<$Res>? get providerAccount {
    if (_value.providerAccount == null) {
      return null;
    }

    return $ProviderAccountCopyWith<$Res>(_value.providerAccount!, (value) {
      return _then(_value.copyWith(providerAccount: value) as $Val);
    });
  }

  @override
  @pragma('vm:prefer-inline')
  $TargetCalendarCopyWith<$Res>? get existingCalendarSelected {
    if (_value.existingCalendarSelected == null) {
      return null;
    }

    return $TargetCalendarCopyWith<$Res>(_value.existingCalendarSelected!,
        (value) {
      return _then(_value.copyWith(existingCalendarSelected: value) as $Val);
    });
  }

  @override
  @pragma('vm:prefer-inline')
  $TargetCalendarCopyWith<$Res>? get newCalendarCreated {
    if (_value.newCalendarCreated == null) {
      return null;
    }

    return $TargetCalendarCopyWith<$Res>(_value.newCalendarCreated!, (value) {
      return _then(_value.copyWith(newCalendarCreated: value) as $Val);
    });
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
  $Res call(
      {NewSyncProfileStep currentStep,
      String title,
      String? titleError,
      String url,
      String? urlError,
      ProviderAccount? providerAccount,
      String? providerAccountError,
      TargetCalendar? existingCalendarSelected,
      TargetCalendar? newCalendarCreated,
      BackendAuthorizationStatus backendAuthorizationStatus,
      String? backendAuthorizationError,
      TargetCalendarChoice targetCalendarChoice,
      bool isSubmitting,
      String? submitError,
      bool submittedSuccessfully});

  @override
  $ProviderAccountCopyWith<$Res>? get providerAccount;
  @override
  $TargetCalendarCopyWith<$Res>? get existingCalendarSelected;
  @override
  $TargetCalendarCopyWith<$Res>? get newCalendarCreated;
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
    Object? currentStep = null,
    Object? title = null,
    Object? titleError = freezed,
    Object? url = null,
    Object? urlError = freezed,
    Object? providerAccount = freezed,
    Object? providerAccountError = freezed,
    Object? existingCalendarSelected = freezed,
    Object? newCalendarCreated = freezed,
    Object? backendAuthorizationStatus = null,
    Object? backendAuthorizationError = freezed,
    Object? targetCalendarChoice = null,
    Object? isSubmitting = null,
    Object? submitError = freezed,
    Object? submittedSuccessfully = null,
  }) {
    return _then(_$NewSyncProfileStateImpl(
      currentStep: null == currentStep
          ? _value.currentStep
          : currentStep // ignore: cast_nullable_to_non_nullable
              as NewSyncProfileStep,
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
      providerAccount: freezed == providerAccount
          ? _value.providerAccount
          : providerAccount // ignore: cast_nullable_to_non_nullable
              as ProviderAccount?,
      providerAccountError: freezed == providerAccountError
          ? _value.providerAccountError
          : providerAccountError // ignore: cast_nullable_to_non_nullable
              as String?,
      existingCalendarSelected: freezed == existingCalendarSelected
          ? _value.existingCalendarSelected
          : existingCalendarSelected // ignore: cast_nullable_to_non_nullable
              as TargetCalendar?,
      newCalendarCreated: freezed == newCalendarCreated
          ? _value.newCalendarCreated
          : newCalendarCreated // ignore: cast_nullable_to_non_nullable
              as TargetCalendar?,
      backendAuthorizationStatus: null == backendAuthorizationStatus
          ? _value.backendAuthorizationStatus
          : backendAuthorizationStatus // ignore: cast_nullable_to_non_nullable
              as BackendAuthorizationStatus,
      backendAuthorizationError: freezed == backendAuthorizationError
          ? _value.backendAuthorizationError
          : backendAuthorizationError // ignore: cast_nullable_to_non_nullable
              as String?,
      targetCalendarChoice: null == targetCalendarChoice
          ? _value.targetCalendarChoice
          : targetCalendarChoice // ignore: cast_nullable_to_non_nullable
              as TargetCalendarChoice,
      isSubmitting: null == isSubmitting
          ? _value.isSubmitting
          : isSubmitting // ignore: cast_nullable_to_non_nullable
              as bool,
      submitError: freezed == submitError
          ? _value.submitError
          : submitError // ignore: cast_nullable_to_non_nullable
              as String?,
      submittedSuccessfully: null == submittedSuccessfully
          ? _value.submittedSuccessfully
          : submittedSuccessfully // ignore: cast_nullable_to_non_nullable
              as bool,
    ));
  }
}

/// @nodoc

class _$NewSyncProfileStateImpl extends _NewSyncProfileState {
  const _$NewSyncProfileStateImpl(
      {this.currentStep = NewSyncProfileStep.title,
      this.title = '',
      this.titleError,
      this.url = '',
      this.urlError,
      this.providerAccount,
      this.providerAccountError = null,
      this.existingCalendarSelected,
      this.newCalendarCreated,
      this.backendAuthorizationStatus =
          BackendAuthorizationStatus.notAuthorized,
      this.backendAuthorizationError,
      this.targetCalendarChoice = TargetCalendarChoice.createNew,
      this.isSubmitting = false,
      this.submitError,
      this.submittedSuccessfully = false})
      : super._();

  @override
  @JsonKey()
  final NewSyncProfileStep currentStep;
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
  final ProviderAccount? providerAccount;
  @override
  @JsonKey()
  final String? providerAccountError;
  @override
  final TargetCalendar? existingCalendarSelected;
  @override
  final TargetCalendar? newCalendarCreated;
  @override
  @JsonKey()
  final BackendAuthorizationStatus backendAuthorizationStatus;
  @override
  final String? backendAuthorizationError;
  @override
  @JsonKey()
  final TargetCalendarChoice targetCalendarChoice;
  @override
  @JsonKey()
  final bool isSubmitting;
  @override
  final String? submitError;
  @override
  @JsonKey()
  final bool submittedSuccessfully;

  @override
  String toString() {
    return 'NewSyncProfileState(currentStep: $currentStep, title: $title, titleError: $titleError, url: $url, urlError: $urlError, providerAccount: $providerAccount, providerAccountError: $providerAccountError, existingCalendarSelected: $existingCalendarSelected, newCalendarCreated: $newCalendarCreated, backendAuthorizationStatus: $backendAuthorizationStatus, backendAuthorizationError: $backendAuthorizationError, targetCalendarChoice: $targetCalendarChoice, isSubmitting: $isSubmitting, submitError: $submitError, submittedSuccessfully: $submittedSuccessfully)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$NewSyncProfileStateImpl &&
            (identical(other.currentStep, currentStep) ||
                other.currentStep == currentStep) &&
            (identical(other.title, title) || other.title == title) &&
            (identical(other.titleError, titleError) ||
                other.titleError == titleError) &&
            (identical(other.url, url) || other.url == url) &&
            (identical(other.urlError, urlError) ||
                other.urlError == urlError) &&
            (identical(other.providerAccount, providerAccount) ||
                other.providerAccount == providerAccount) &&
            (identical(other.providerAccountError, providerAccountError) ||
                other.providerAccountError == providerAccountError) &&
            (identical(
                    other.existingCalendarSelected, existingCalendarSelected) ||
                other.existingCalendarSelected == existingCalendarSelected) &&
            (identical(other.newCalendarCreated, newCalendarCreated) ||
                other.newCalendarCreated == newCalendarCreated) &&
            (identical(other.backendAuthorizationStatus,
                    backendAuthorizationStatus) ||
                other.backendAuthorizationStatus ==
                    backendAuthorizationStatus) &&
            (identical(other.backendAuthorizationError,
                    backendAuthorizationError) ||
                other.backendAuthorizationError == backendAuthorizationError) &&
            (identical(other.targetCalendarChoice, targetCalendarChoice) ||
                other.targetCalendarChoice == targetCalendarChoice) &&
            (identical(other.isSubmitting, isSubmitting) ||
                other.isSubmitting == isSubmitting) &&
            (identical(other.submitError, submitError) ||
                other.submitError == submitError) &&
            (identical(other.submittedSuccessfully, submittedSuccessfully) ||
                other.submittedSuccessfully == submittedSuccessfully));
  }

  @override
  int get hashCode => Object.hash(
      runtimeType,
      currentStep,
      title,
      titleError,
      url,
      urlError,
      providerAccount,
      providerAccountError,
      existingCalendarSelected,
      newCalendarCreated,
      backendAuthorizationStatus,
      backendAuthorizationError,
      targetCalendarChoice,
      isSubmitting,
      submitError,
      submittedSuccessfully);

  @JsonKey(ignore: true)
  @override
  @pragma('vm:prefer-inline')
  _$$NewSyncProfileStateImplCopyWith<_$NewSyncProfileStateImpl> get copyWith =>
      __$$NewSyncProfileStateImplCopyWithImpl<_$NewSyncProfileStateImpl>(
          this, _$identity);
}

abstract class _NewSyncProfileState extends NewSyncProfileState {
  const factory _NewSyncProfileState(
      {final NewSyncProfileStep currentStep,
      final String title,
      final String? titleError,
      final String url,
      final String? urlError,
      final ProviderAccount? providerAccount,
      final String? providerAccountError,
      final TargetCalendar? existingCalendarSelected,
      final TargetCalendar? newCalendarCreated,
      final BackendAuthorizationStatus backendAuthorizationStatus,
      final String? backendAuthorizationError,
      final TargetCalendarChoice targetCalendarChoice,
      final bool isSubmitting,
      final String? submitError,
      final bool submittedSuccessfully}) = _$NewSyncProfileStateImpl;
  const _NewSyncProfileState._() : super._();

  @override
  NewSyncProfileStep get currentStep;
  @override
  String get title;
  @override
  String? get titleError;
  @override
  String get url;
  @override
  String? get urlError;
  @override
  ProviderAccount? get providerAccount;
  @override
  String? get providerAccountError;
  @override
  TargetCalendar? get existingCalendarSelected;
  @override
  TargetCalendar? get newCalendarCreated;
  @override
  BackendAuthorizationStatus get backendAuthorizationStatus;
  @override
  String? get backendAuthorizationError;
  @override
  TargetCalendarChoice get targetCalendarChoice;
  @override
  bool get isSubmitting;
  @override
  String? get submitError;
  @override
  bool get submittedSuccessfully;
  @override
  @JsonKey(ignore: true)
  _$$NewSyncProfileStateImplCopyWith<_$NewSyncProfileStateImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
