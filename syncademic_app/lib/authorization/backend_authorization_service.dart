import 'dart:developer';

import 'package:syncademic_app/models/provider_account.dart';

abstract class BackendAuthorizationService {
  /// Authorizes the backend using the given [providerAccount].
  /// Throws an exception if the authorization fails.
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
