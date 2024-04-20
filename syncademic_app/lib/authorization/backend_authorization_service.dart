import 'dart:developer';

abstract class BackendAuthorizationService {
  Future<void> authorizeBackend();
}

class MockBackendAuthorizationService implements BackendAuthorizationService {
  @override
  Future<void> authorizeBackend() async {
    log("Authorizing the backend using a mock service");
  }
}
