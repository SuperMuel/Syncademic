import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:google_sign_in/google_sign_in.dart';
import 'package:googleapis/calendar/v3.dart';
import 'package:http/http.dart' as http;

abstract class AuthorizationService {
  Future<bool> isAuthorized();
  Future<bool> authorize();
  Future<http.Client> get client;
}

class MockAuthorizationService implements AuthorizationService {
  @override
  Future<bool> authorize() => Future.value(true);

  @override
  Future<bool> isAuthorized() => Future.value(true);

  @override
  Future<http.Client> get client => Future.value(http.Client());
}

final _scopes = [CalendarApi.calendarScope, CalendarApi.calendarEventsScope];

class GoogleAuthorizationService implements AuthorizationService {
  final GoogleSignIn _googleSignIn;

  GoogleAuthorizationService({GoogleSignIn? googleSignIn})
      : _googleSignIn = googleSignIn ??
            GoogleSignIn(
              scopes: _scopes,
              clientId: dotenv.env['SYNCADEMIA_CLIENT_ID'],
            );

  @override
  Future<bool> authorize() => _googleSignIn.requestScopes(_scopes);

  @override
  Future<bool> isAuthorized() => _googleSignIn.canAccessScopes(_scopes);

  @override
  // TODO: implement client
  Future<http.Client> get client =>
      throw UnimplementedError(); // This only works on web
}
