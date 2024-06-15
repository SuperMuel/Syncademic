import 'package:google_sign_in/google_sign_in.dart';

import 'package:google_sign_in_web/web_only.dart';
import 'package:syncademic_app/authorization/google_authorization/google_authorization_service.dart';

import '../../authorization_service.dart';

class GoogleAuthorizationServiceImpl implements AuthorizationService {
  final GoogleSignIn googleSignIn;

  GoogleAuthorizationServiceImpl({required this.googleSignIn});

  @override
  Future<String?> getAuthorizationCode(String providerAccountId) async {
    final currentUser = await googleSignIn.getCurrentUserOrSignIn();

    if (currentUser == null) {
      throw Exception('User not logged in');
    }

    if (currentUser.id != providerAccountId) {
      throw UserIdMismatchException();
    }

    return await requestServerAuthCode();
  }
}
