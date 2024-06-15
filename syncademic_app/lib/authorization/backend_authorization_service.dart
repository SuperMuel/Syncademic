import 'dart:developer';

import '../models/provider_account.dart';

/// Thrown when the user ID of the currently signed-in user does not match the
/// ID of the provider account associated with the sync profile that requests
/// the authorization.
class ProviderUserIdMismatchException implements Exception {
  final String message;

  ProviderUserIdMismatchException(
      [this.message =
          'The user might have selected the wrong account in the authorization popup.']);

  @override
  String toString() => message;
}

abstract class BackendAuthorizationService {
  /// Authorizes the backend using the given [providerAccount].
  /// Throws an exception if the authorization fails.
  /// If the user authorized the backend using a different account than [providerAccount],
  /// throws a [ProviderUserIdMismatchException].
  Future<void> authorizeBackend(ProviderAccount providerAccount);

  Future<bool> isAuthorized(ProviderAccount providerAccount);
}

class MockBackendAuthorizationService implements BackendAuthorizationService {
  @override
  Future<void> authorizeBackend(ProviderAccount providerAccount) async {
    log("Authorizing the backend using a mock service");
  }

  @override
  Future<bool> isAuthorized(ProviderAccount providerAccount) async {
    await Future.delayed(const Duration(microseconds: 1));
    return true;
  }
}
