import 'dart:developer';

import 'package:cloud_functions/cloud_functions.dart';
import 'package:fpdart/fpdart.dart';

class IcsValidationResult {
  final bool isValid;
  final String? error;
  final int? nbEvents;

  IcsValidationResult({
    required this.isValid,
    required this.error,
    required this.nbEvents,
  });
}

abstract class IcsValidationService {
  const IcsValidationService();

  Future<Either<String, IcsValidationResult>> validateUrl(String url);
}

class FirebaseIcsValidationService extends IcsValidationService {
  const FirebaseIcsValidationService();

  @override
  Future<Either<String, IcsValidationResult>> validateUrl(String url) async {
    log('Validating URL: $url');

    late HttpsCallableResult response;

    try {
      response = await FirebaseFunctions.instance
          .httpsCallable('validate_ics_url')
          .call(
        {'url': url},
      );
    } catch (e) {
      log('Error while validating URL: $e');
      return left(e.toString());
    }

    log('Validation result: ${response.data}');

    try {
      //TODO : parse using deep_pick https://pub.dev/packages/deep_pick
      final result = IcsValidationResult(
        isValid: response.data['valid'],
        nbEvents: response.data.containsKey('nbEvents')
            ? response.data['nbEvents']
            : null,
        error: response.data['error'],
      );
      return right(result);
    } catch (e) {
      log('Error while parsing validation result: $e');
      return left(e.toString());
    }
  }
}

class MockIcsValidationService extends IcsValidationService {
  const MockIcsValidationService();

  @override
  Future<Either<String, IcsValidationResult>> validateUrl(String url) async {
    // Simulate network delay
    await Future.delayed(const Duration(milliseconds: 500));

    return right(IcsValidationResult(
      isValid: true,
      error: null,
      nbEvents: 42, // Mock number of events
    ));
  }
}
