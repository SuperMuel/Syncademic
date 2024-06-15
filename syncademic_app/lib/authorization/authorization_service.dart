import 'dart:async';

import 'package:googleapis/calendar/v3.dart';

abstract class AuthorizationService {
  Future<String?> getAuthorizationCode(String providerAccountId);
}

class MockAuthorizationService implements AuthorizationService {
  @override
  Future<String> getAuthorizationCode(String providerAccountId) =>
      Future.delayed(const Duration(microseconds: 1))
          .then((_) => 'mock-auth-code');
}

final scopes = [CalendarApi.calendarScope];
