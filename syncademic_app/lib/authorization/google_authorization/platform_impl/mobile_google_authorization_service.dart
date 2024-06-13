import 'dart:developer';

import 'package:google_sign_in/google_sign_in.dart';

import '../../authorization_service.dart';

class GoogleAuthorizationServiceImpl implements AuthorizationService {
  final GoogleSignIn googleSignIn;
  GoogleSignInAccount? _currentUser;
  String? _lastAuthorizationCode;

  GoogleAuthorizationServiceImpl({required this.googleSignIn});

  @override
  Future<String?> getAuthorizationCode(String providerAccountId) async {
    // It is not nessary to sign in again if the user is already signed in to get a first authorization code.
    // However, if a second authorization code is requested, the user must be signed in again to get a different code.
    if (_lastAuthorizationCode != null) {
      log("To get a different authorization code, the user will be signed out and will have to sign in again.");
      await googleSignIn.signOut();
      _currentUser = null;
    }

    _currentUser ??= await googleSignIn.signIn();

    if (_currentUser == null) {
      throw Exception(
          "User not logged in. Authorization code cannot be retrieved.");
    }

    if (_currentUser!.id != providerAccountId) {
      throw UserIdMismatchException();
    }

    final authCode = _currentUser!.serverAuthCode;
    _lastAuthorizationCode = authCode;

    return authCode;
  }
}
