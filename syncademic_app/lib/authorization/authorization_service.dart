import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:google_sign_in/google_sign_in.dart';
import 'package:googleapis/calendar/v3.dart';

abstract class AuthorizationService {
  Future<bool> isAuthorized();
  Future<bool> authorize();
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
  Future<bool> isAuthorized() =>
      _googleSignIn.canAccessScopes(_scopes); // This only works on web
}
