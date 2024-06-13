import 'dart:async';

import 'package:googleapis/calendar/v3.dart';

/// Thrown when the user ID of the currently signed-in user does not match the
/// ID of the provider account associated with the sync profile that requests
/// the authorization.
class UserIdMismatchException implements Exception {
  final String message;

  UserIdMismatchException(
      [this.message =
          'Current logged-in User does not match the provider account ID']);

  @override
  String toString() => message;
}

abstract class AuthorizationService {
  /// throws UserIdMismatchException
  Future<String?> getAuthorizationCode(String providerAccountId);
}

class MockAuthorizationService implements AuthorizationService {
  @override
  Future<String> getAuthorizationCode(String providerAccountId) =>
      Future.delayed(const Duration(microseconds: 1))
          .then((_) => 'mock-auth-code');
}

final scopes = [CalendarApi.calendarScope];
