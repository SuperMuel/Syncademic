import 'dart:developer';

import 'package:fpdart/fpdart.dart';
import 'package:get_it/get_it.dart';

import '../backend/backend_api.dart';

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

class BackendIcsValidationService extends IcsValidationService {
  BackendIcsValidationService({BackendApi? backendApi})
      : _backendApi = backendApi ?? GetIt.I.get<BackendApi>();

  final BackendApi _backendApi;

  @override
  Future<Either<String, IcsValidationResult>> validateUrl(String url) async {
    log('Validating URL: $url');
    try {
      final response = await _backendApi.validateIcsUrl(url);
      log('Validation result: $response');

      final result = IcsValidationResult(
        isValid: response.isValid,
        nbEvents: response.nbEvents,
        error: response.error,
      );
      return right(result);
    } on BackendApiException catch (e) {
      log('Backend API error while validating URL: ${e.message}');
      return left(e.message);
    } catch (e) {
      log('Error while validating URL: $e');
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
