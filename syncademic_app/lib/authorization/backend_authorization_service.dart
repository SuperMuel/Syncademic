import 'dart:developer';

import 'package:cloud_functions/cloud_functions.dart';
import 'package:get_it/get_it.dart';
import 'package:syncademic_app/authorization/authorization_service.dart';

abstract class BackendAuthorizationService {
  Future<void> authorizeBackend(String syncProfileId);
}

class FirebaseBackendAuthorizationService
    implements BackendAuthorizationService {
  @override
  Future<void> authorizeBackend(String syncProfileId) async {
    log("Authorizing the backend using Firebase");

    final authCode =
        await GetIt.I.get<AuthorizationService>().getAuthorizationCode();

    if (authCode == null) {
      log('Authorization code is null !');
      return;
    }

    log("Got authorization code. Sending it to the backend.");

    try {
      await FirebaseFunctions.instance.httpsCallable('authorize_backend').call({
        'authCode': authCode,
        'syncProfileId': syncProfileId,
      });
    } on FirebaseFunctionsException catch (e) {
      log('Error authorizing backend: ${e.code}, ${e.details}, ${e.message}');
      rethrow;
    }
  }
}
