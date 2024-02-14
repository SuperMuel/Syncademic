part of 'auth_cubit.dart';

@freezed
class AuthState with _$AuthState {
  const factory AuthState.authenticated(User user) = _Authenticated;

  const factory AuthState.unauthenticated() = _Unauthenticated;

  const factory AuthState.loading() = _Loading;
}
