// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'provider_account.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

/// @nodoc
mixin _$ProviderAccount {
  /// The ID of the provider account, unique within Syncademic.
  ID? get id => throw _privateConstructorUsedError;

  /// The provider of the account (e.g., Google).
  Provider get provider => throw _privateConstructorUsedError;

  /// The unique ID of the account on the provider's service.
  String get providerAccountId => throw _privateConstructorUsedError;

  /// The email address associated with the account on the provider's service.
  String get providerAccountEmail => throw _privateConstructorUsedError;

  @JsonKey(ignore: true)
  $ProviderAccountCopyWith<ProviderAccount> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ProviderAccountCopyWith<$Res> {
  factory $ProviderAccountCopyWith(
          ProviderAccount value, $Res Function(ProviderAccount) then) =
      _$ProviderAccountCopyWithImpl<$Res, ProviderAccount>;
  @useResult
  $Res call(
      {ID? id,
      Provider provider,
      String providerAccountId,
      String providerAccountEmail});
}

/// @nodoc
class _$ProviderAccountCopyWithImpl<$Res, $Val extends ProviderAccount>
    implements $ProviderAccountCopyWith<$Res> {
  _$ProviderAccountCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = freezed,
    Object? provider = null,
    Object? providerAccountId = null,
    Object? providerAccountEmail = null,
  }) {
    return _then(_value.copyWith(
      id: freezed == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as ID?,
      provider: null == provider
          ? _value.provider
          : provider // ignore: cast_nullable_to_non_nullable
              as Provider,
      providerAccountId: null == providerAccountId
          ? _value.providerAccountId
          : providerAccountId // ignore: cast_nullable_to_non_nullable
              as String,
      providerAccountEmail: null == providerAccountEmail
          ? _value.providerAccountEmail
          : providerAccountEmail // ignore: cast_nullable_to_non_nullable
              as String,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$ProviderAccountImplCopyWith<$Res>
    implements $ProviderAccountCopyWith<$Res> {
  factory _$$ProviderAccountImplCopyWith(_$ProviderAccountImpl value,
          $Res Function(_$ProviderAccountImpl) then) =
      __$$ProviderAccountImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {ID? id,
      Provider provider,
      String providerAccountId,
      String providerAccountEmail});
}

/// @nodoc
class __$$ProviderAccountImplCopyWithImpl<$Res>
    extends _$ProviderAccountCopyWithImpl<$Res, _$ProviderAccountImpl>
    implements _$$ProviderAccountImplCopyWith<$Res> {
  __$$ProviderAccountImplCopyWithImpl(
      _$ProviderAccountImpl _value, $Res Function(_$ProviderAccountImpl) _then)
      : super(_value, _then);

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = freezed,
    Object? provider = null,
    Object? providerAccountId = null,
    Object? providerAccountEmail = null,
  }) {
    return _then(_$ProviderAccountImpl(
      id: freezed == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as ID?,
      provider: null == provider
          ? _value.provider
          : provider // ignore: cast_nullable_to_non_nullable
              as Provider,
      providerAccountId: null == providerAccountId
          ? _value.providerAccountId
          : providerAccountId // ignore: cast_nullable_to_non_nullable
              as String,
      providerAccountEmail: null == providerAccountEmail
          ? _value.providerAccountEmail
          : providerAccountEmail // ignore: cast_nullable_to_non_nullable
              as String,
    ));
  }
}

/// @nodoc

class _$ProviderAccountImpl extends _ProviderAccount {
  const _$ProviderAccountImpl(
      {required this.id,
      required this.provider,
      required this.providerAccountId,
      required this.providerAccountEmail})
      : super._();

  /// The ID of the provider account, unique within Syncademic.
  @override
  final ID? id;

  /// The provider of the account (e.g., Google).
  @override
  final Provider provider;

  /// The unique ID of the account on the provider's service.
  @override
  final String providerAccountId;

  /// The email address associated with the account on the provider's service.
  @override
  final String providerAccountEmail;

  @override
  String toString() {
    return 'ProviderAccount(id: $id, provider: $provider, providerAccountId: $providerAccountId, providerAccountEmail: $providerAccountEmail)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ProviderAccountImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.provider, provider) ||
                other.provider == provider) &&
            (identical(other.providerAccountId, providerAccountId) ||
                other.providerAccountId == providerAccountId) &&
            (identical(other.providerAccountEmail, providerAccountEmail) ||
                other.providerAccountEmail == providerAccountEmail));
  }

  @override
  int get hashCode => Object.hash(
      runtimeType, id, provider, providerAccountId, providerAccountEmail);

  @JsonKey(ignore: true)
  @override
  @pragma('vm:prefer-inline')
  _$$ProviderAccountImplCopyWith<_$ProviderAccountImpl> get copyWith =>
      __$$ProviderAccountImplCopyWithImpl<_$ProviderAccountImpl>(
          this, _$identity);
}

abstract class _ProviderAccount extends ProviderAccount {
  const factory _ProviderAccount(
      {required final ID? id,
      required final Provider provider,
      required final String providerAccountId,
      required final String providerAccountEmail}) = _$ProviderAccountImpl;
  const _ProviderAccount._() : super._();

  @override

  /// The ID of the provider account, unique within Syncademic.
  ID? get id;
  @override

  /// The provider of the account (e.g., Google).
  Provider get provider;
  @override

  /// The unique ID of the account on the provider's service.
  String get providerAccountId;
  @override

  /// The email address associated with the account on the provider's service.
  String get providerAccountEmail;
  @override
  @JsonKey(ignore: true)
  _$$ProviderAccountImplCopyWith<_$ProviderAccountImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
