import 'dart:async';

import 'package:googleapis/calendar/v3.dart';
import 'package:http/http.dart' as http;

abstract class AuthorizationService {
  Future<bool> isAuthorized();
  Future<bool> authorize();
  Future<http.Client?> get authorizedClient;

  /// Returns the user ID of the currently authorized user.
  ///
  /// Note that this ID may not match the ID of the currently signed-in user.
  /// This is because a single user can establish multiple sync profiles,
  /// each potentially associated with a different calendar service.
  Future<String?> get userId;
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
  Future<String?> getAuthorizationCode() => Future.value('mocked_auth_code');

  @override
  Future<String?> get userId => Future.value('mocked_user_id');
}

final scopes = [CalendarApi.calendarScope];
