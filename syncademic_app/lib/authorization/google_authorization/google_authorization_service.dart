import 'package:google_sign_in/google_sign_in.dart';

import '../authorization_service.dart';

import 'platform_impl/stub_google_authorization_service.dart' // https://gpalma.pt/blog/conditional-importing/
    if (dart.library.io) 'platform_impl/mobile_google_authorization_service.dart'
    if (dart.library.html) 'platform_impl/web_google_authorization_service.dart';

class GoogleAuthorizationService implements AuthorizationService {
  final GoogleAuthorizationServiceImpl _impl;

  GoogleAuthorizationService({
    required GoogleSignIn googleSignIn,
  }) : _impl = GoogleAuthorizationServiceImpl(googleSignIn: googleSignIn);

  @override
  Future<String?> getAuthorizationCode(String providerAccountId) {
    return _impl.getAuthorizationCode(providerAccountId);
  }
}

extension GoogleSignInAccountExtension on GoogleSignIn {
  Future<GoogleSignInAccount?> getCurrentUserOrSignIn() async =>
      currentUser ?? await signIn();
}
