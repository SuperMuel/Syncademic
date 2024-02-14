import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:get_it/get_it.dart';

import '../../models/user.dart';
import '../../services/auth_service.dart';

part 'auth_cubit.freezed.dart';
part 'auth_state.dart';

class AuthCubit extends Cubit<AuthState> {
  late final AuthService _authService;

  AuthCubit({AuthService? authService})
      : super(const AuthState.unauthenticated()) {
    _authService = authService ?? GetIt.I<AuthService>();
    _authService.authStateChanges.listen(_userChanged);
  }

  void _userChanged(User? user) {
    if (user != null) {
      emit(AuthState.authenticated(user));
    } else {
      print('unauthenticated');
      emit(const AuthState.unauthenticated());
    }
  }

  Future<void> signInWithGoogle() async {
    emit(const AuthState.loading());
    await _authService.signInWithGoogle();
  }

  Future<void> signOut() async {
    emit(const AuthState.loading());
    await _authService.signOut();
  }
}
