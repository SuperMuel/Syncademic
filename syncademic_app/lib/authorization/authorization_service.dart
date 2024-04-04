import 'dart:async';
import 'package:google_sign_in_web/web_only.dart';
import 'dart:convert';
import 'dart:developer';

import 'package:extension_google_sign_in_as_googleapis_auth/extension_google_sign_in_as_googleapis_auth.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:google_sign_in/google_sign_in.dart';
import 'package:google_sign_in_platform_interface/google_sign_in_platform_interface.dart';
import 'package:googleapis/calendar/v3.dart';
import 'package:http/http.dart' as http;

abstract class AuthorizationService {
  Future<bool> isAuthorized();
  Future<bool> authorize();
  Future<http.Client?> get authorizedClient;
  Future<String?> get accessToken;
  Future<String?> getAuthorizationCode();
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

  @override
  Future<String?> getAuthorizationCode() => Future.value('mocked_auth_code');
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
              forceCodeForRefreshToken: true,
            );

  @override
  Future<String?> getAuthorizationCode() async {
    _currentUser = await _googleSignIn.signIn();
    if (_currentUser == null) {
      log('User not logged in');
      return null;
    }

    final authCode = await requestServerAuthCode();

    log('Sucessfully got authCode');

    return authCode;
  }

  @override
  Future<bool> authorize() async {
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
