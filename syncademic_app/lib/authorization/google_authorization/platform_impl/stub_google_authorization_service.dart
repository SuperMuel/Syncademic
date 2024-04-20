import 'package:google_sign_in/google_sign_in.dart';
import 'package:http/http.dart' as http;
import 'package:syncademic_app/authorization/authorization_service.dart';

class GoogleAuthorizationServiceImpl implements AuthorizationService {
  GoogleAuthorizationServiceImpl({GoogleSignIn? googleSignIn}) {
    throw Exception('Stub constructor');
  }

  @override
  Future<String?> getAuthorizationCode() async {
    throw Exception('Stub method');
  }

  @override
  Future<bool> authorize() async {
    throw Exception('Stub method');
  }

  @override
  Future<bool> isAuthorized() {
    throw Exception('Stub method');
  }

  @override
  Future<http.Client?> get authorizedClient {
    throw Exception('Stub method');
  }

  @override
  Future<String?> get userId async {
    throw Exception('Stub method');
  }
}
