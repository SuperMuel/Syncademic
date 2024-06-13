import 'package:google_sign_in/google_sign_in.dart';

import 'package:google_sign_in_web/web_only.dart';

import '../../authorization_service.dart';

class GoogleAuthorizationServiceImpl implements AuthorizationService {
  final GoogleSignIn googleSignIn;

  GoogleAuthorizationServiceImpl({required this.googleSignIn});

  @override
  Future<String?> getAuthorizationCode(String providerAccountId) async {
    final currentUser = await googleSignIn.signIn();

    if (currentUser == null) {
      throw Exception('User not logged in');
    }

    if (currentUser.id != providerAccountId) {
      throw UserIdMismatchException();
    }

    return await requestServerAuthCode();
  }
}
