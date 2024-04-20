import 'dart:developer';

import 'package:extension_google_sign_in_as_googleapis_auth/extension_google_sign_in_as_googleapis_auth.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:google_sign_in/google_sign_in.dart';
import 'package:google_sign_in_web/web_only.dart';
import 'package:http/http.dart' as http;
import 'authorization_service.dart';

class GoogleAuthorizationService implements AuthorizationService {
  final GoogleSignIn _googleSignIn;
  GoogleSignInAccount? _currentUser;

  GoogleAuthorizationService({GoogleSignIn? googleSignIn})
      : _googleSignIn = googleSignIn ??
            GoogleSignIn(
              scopes: scopes,
              clientId: dotenv.env['SYNCADEMIC_CLIENT_ID'],
            );

  @override
  Future<String?> getAuthorizationCode() async {
    //TODO: Check if signIn is necessary. If so, write it here.
    _currentUser = await _googleSignIn.signIn();
    if (_currentUser == null) {
      log('User not logged in');
      return null;
    }

    return await requestServerAuthCode();
  }

  @override
  Future<bool> authorize() async {
    //TODO : check if canAccessScopes before authorizing again
    _currentUser = await _googleSignIn.signIn();
    return _currentUser != null;
  }

  @override
  Future<bool> isAuthorized() => _googleSignIn.canAccessScopes(scopes);

  @override
  Future<http.Client?> get authorizedClient =>
      _googleSignIn.authenticatedClient();

  @override
  Future<String?> get userId async => _currentUser?.id;
}
