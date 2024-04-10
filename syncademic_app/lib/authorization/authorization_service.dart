import 'dart:async';

import 'package:extension_google_sign_in_as_googleapis_auth/extension_google_sign_in_as_googleapis_auth.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:google_sign_in/google_sign_in.dart';
import 'package:googleapis/calendar/v3.dart';
import 'package:http/http.dart' as http;

abstract class AuthorizationService {
  Future<bool> isAuthorized();
  Future<bool> authorize();
  Future<http.Client?> get authorizedClient;
  Future<String?> get accessToken;
}

class MockAuthorizationService implements AuthorizationService {
  @override
  Future<bool> authorize() => Future.value(true);

  @override
  Future<bool> isAuthorized() => Future.value(true);

  @override
  Future<http.Client> get authorizedClient => Future.value(http.Client());

  @override
  Future<String?> get accessToken => Future.value(null);
}

final _scopes = [CalendarApi.calendarScope];

class GoogleAuthorizationService implements AuthorizationService {
  final GoogleSignIn _googleSignIn;
  GoogleSignInAccount? _currentUser;

  GoogleAuthorizationService({GoogleSignIn? googleSignIn})
      : _googleSignIn = googleSignIn ??
            GoogleSignIn(
              scopes: _scopes,
              clientId: dotenv.env['SYNCADEMIC_CLIENT_ID'],
            );

  @override
  Future<bool> authorize() async {
    // TODO : Is it necessary to signout before signing in? (To be sure that the user can select the right account)
    _currentUser = await _googleSignIn.signIn();
    return _currentUser != null;
  }

  @override
  Future<bool> isAuthorized() => _googleSignIn.canAccessScopes(_scopes);

  @override
  Future<String?> get accessToken async {
    if (_currentUser == null) {
      // TODO(SuperMuel) Log error
      return null;
    }

    final headers = await _currentUser!.authHeaders;

    // strip the "Bearer " prefix
    return headers['Authorization']?.substring(7);
  }

  @override
  Future<http.Client?> get authorizedClient =>
      _googleSignIn.authenticatedClient();
}
