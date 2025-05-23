import 'dart:developer';

import 'package:cloud_functions/cloud_functions.dart';
import 'package:get_it/get_it.dart';

import '../models/provider_account.dart';
import 'authorization_service.dart';
import 'backend_authorization_service.dart';

class FirebaseBackendAuthorizationService
    implements BackendAuthorizationService {
  final String redirectUri;
  final FirebaseFunctions functions;

  FirebaseBackendAuthorizationService({
    required this.redirectUri,
  }) : functions = GetIt.I<FirebaseFunctions>();

  @override
  Future<void> authorizeBackend(ProviderAccount providerAccount) async {
    log("Authorizing the backend using Firebase");

    final authCode = await GetIt.I
        .get<AuthorizationService>()
        .getAuthorizationCode(providerAccount.providerAccountId);

    if (authCode == null) {
      log('Authorization code is null !');
      throw Exception('Authorization code is null');
    }

    log("Got authorization code. Sending it to the backend.");

    try {
      await functions.httpsCallable('authorize_backend').call({
        'provider': providerAccount.provider.name,
        'providerAccountId': providerAccount.providerAccountId,
        'authCode': authCode,
        'redirectUri': redirectUri,
      });
    } on FirebaseFunctionsException catch (e) {
      log('Error authorizing backend: ${e.code}, ${e.details}, ${e.message}');
      if (e.message != null && e.message!.contains('ProviderUserIdMismatch')) {
        throw ProviderUserIdMismatchException();
      }
      rethrow;
    }
  }

  @override
  Future<bool> isAuthorized(ProviderAccount providerAccount) async {
    final result = await functions.httpsCallable('is_authorized').call({
      'providerAccountId': providerAccount.providerAccountId,
    });

    return result.data['authorized'];
  }
}
