import 'package:google_sign_in/google_sign_in.dart';

import '../authorization_service.dart';
import 'platform_impl/stub_google_authorization_service.dart'
    if (dart.library.io) 'platform_impl/mobile_google_authorization_service.dart'
    if (dart.library.html) 'platform_impl/web_google_authorization_service.dart';

import 'package:http/http.dart' as http;

class GoogleAuthorizationService implements AuthorizationService {
  final GoogleAuthorizationServiceImpl _impl;

  GoogleAuthorizationService({
    GoogleSignIn? googleSignIn,
  }) : _impl = GoogleAuthorizationServiceImpl(googleSignIn: googleSignIn);

  @override
  Future<String?> getAuthorizationCode() {
    return _impl.getAuthorizationCode();
  }

  @override
  Future<bool> authorize() {
    return _impl.authorize();
  }

  @override
  Future<bool> isAuthorized() {
    return _impl.isAuthorized();
  }

  @override
  Future<String?> get userId async {
    return _impl.userId;
  }

  @override
  Future<http.Client?> get authorizedClient {
    return _impl.authorizedClient;
  }
}
