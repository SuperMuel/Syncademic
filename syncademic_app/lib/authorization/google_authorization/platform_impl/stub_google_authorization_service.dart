import 'package:google_sign_in/google_sign_in.dart';

import '../../authorization_service.dart';

class GoogleAuthorizationServiceImpl implements AuthorizationService {
  GoogleAuthorizationServiceImpl({GoogleSignIn? googleSignIn}) {
    throw Exception('Stub constructor');
  }

  @override
  Future<String?> getAuthorizationCode(String providerAccountId) async {
    throw Exception('Stub method');
  }
}
