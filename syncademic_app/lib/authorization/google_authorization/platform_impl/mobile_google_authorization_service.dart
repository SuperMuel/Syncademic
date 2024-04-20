import 'dart:developer';

import 'package:extension_google_sign_in_as_googleapis_auth/extension_google_sign_in_as_googleapis_auth.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:google_sign_in/google_sign_in.dart';

import 'package:http/http.dart' as http;

import '../../authorization_service.dart';

class GoogleAuthorizationServiceImpl implements AuthorizationService {
  final GoogleSignIn _googleSignIn;
  GoogleSignInAccount? _currentUser;
  String? _lastAuthorizationCode;

  GoogleAuthorizationServiceImpl({GoogleSignIn? googleSignIn})
      : _googleSignIn = googleSignIn ??
            GoogleSignIn(
              scopes: scopes,
              forceCodeForRefreshToken: true,
              serverClientId: dotenv.env['SYNCADEMIC_CLIENT_ID'],
            );

  @override
  Future<String?> getAuthorizationCode() async {
    // It is not nessary to sign in again if the user is already signed in to get a first authorization code.
    // However, if a second authorization code is requested, the user must be signed in again to get a different code.
    if (_lastAuthorizationCode != null) {
      log("To get a different authorization code, the user will be signed out and will have to sign in again.");
      await _googleSignIn.signOut();
      _currentUser = null;
    }

    _currentUser ??= await _googleSignIn.signIn();

    if (_currentUser == null) {
      throw Exception(
          "User not logged in. Authorization code cannot be retrieved.");
    }

    final authCode = _currentUser!.serverAuthCode;
    _lastAuthorizationCode = authCode;

    return authCode;
  }

  @override
  Future<bool> authorize() async {
    log("Authorizing on mobile");

    if (_googleSignIn.currentUser != null) {
      log("""
Authorization request while a user is already signed in. Google documentation says it will not prompt the user again,
but return the same user. If this is not the desired behavior, sign out the user first.""");
    }

    _currentUser = await _googleSignIn.signIn();
    return _currentUser != null;
  }

  @override
  Future<bool> isAuthorized() {
    log("Checking if authorized on mobile");

    // _googleSignIn.canAccessScopes(scopes); // Is not implemented on mobile.
    return _googleSignIn.isSignedIn();
  }

  @override
  Future<http.Client?> get authorizedClient =>
      _googleSignIn.authenticatedClient();

  @override
  Future<String?> get userId async => _currentUser?.id;
}
