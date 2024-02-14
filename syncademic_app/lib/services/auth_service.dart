import 'dart:async';

import '../models/user.dart';

abstract class AuthService {
  /// Signs in with Google and returns a [User] on success.
  Future<User?> signInWithGoogle();

  /// Signs out the current user.
  Future<void> signOut();

  /// A stream of [User] that will provide the current user when the authentication state changes.
  Stream<User?> get authStateChanges;

  /// Gets the current user, or null if no user is signed in.
  Future<User?> get currentUser;
}

class MockAuthService implements AuthService {
  User? _currentUser;

  final _userController = StreamController<User?>.broadcast();

  @override
  Future<User> signInWithGoogle() async {
    await Future.delayed(const Duration(seconds: 1));
    _currentUser = User(id: 'mock-user-id');
    _userController.add(_currentUser!);
    return _currentUser!;
  }

  @override
  Future<void> signOut() async {
    await Future.delayed(const Duration(seconds: 1));
    _currentUser = null;
    _userController.add(null);
  }

  @override
  Stream<User?> get authStateChanges => _userController.stream;

  @override
  Future<User?> get currentUser async {
    await Future.delayed(const Duration(milliseconds: 500));
    return _currentUser;
  }

  void dispose() {
    _userController.close();
  }
}
