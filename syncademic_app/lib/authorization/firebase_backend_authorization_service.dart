import 'dart:developer';

import 'package:cloud_functions/cloud_functions.dart';
import 'package:get_it/get_it.dart';
import 'authorization_service.dart';
import 'backend_authorization_service.dart';

class FirebaseBackendAuthorizationService
    implements BackendAuthorizationService {
  final String redirectUri;

  FirebaseBackendAuthorizationService(
      {this.redirectUri = 'https://syncademic.io'});

  @override
  Future<void> authorizeBackend() async {
    log("Authorizing the backend using Firebase");

    final authCode =
        await GetIt.I.get<AuthorizationService>().getAuthorizationCode();

    if (authCode == null) {
      log('Authorization code is null !');
      throw Exception('Authorization code is null');
    }

    log("Got authorization code. Sending it to the backend.");

    try {
      await FirebaseFunctions.instance.httpsCallable('authorize_backend').call({
        'authCode': authCode,
        'redirectUri': redirectUri,
      });
    } on FirebaseFunctionsException catch (e) {
      log('Error authorizing backend: ${e.code}, ${e.details}, ${e.message}');
      rethrow;
    }
  }
}
