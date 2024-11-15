import 'dart:developer';

import 'package:cloud_functions/cloud_functions.dart';
import 'package:fpdart/fpdart.dart';

class IcsValidationResult {
  final bool isValid;
  final String? error;
  final int? nbEvents;

  IcsValidationResult({
    required this.isValid,
    this.error,
    this.nbEvents,
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

    late HttpsCallableResult result;

    try {
      result = await FirebaseFunctions.instance
          .httpsCallable('validate_ics_url')
          .call(
        {'url': url},
      );
    } catch (e) {
      log('Error while validating URL: $e');
      return left(e.toString());
    }

    log('Validation result: ${result.data}');

    return right(IcsValidationResult(
      isValid: result.data['valid'],
      nbEvents: result.data['nbEvents'],
      error: result.data['error'],
    ));
  }
}
