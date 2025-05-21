import 'dart:developer'; // Keep for logging

import 'package:cloud_functions/cloud_functions.dart';
import 'package:fpdart/fpdart.dart';
import 'package:get_it/get_it.dart';

// Remove http and firebase_auth imports if no longer directly needed
// import 'dart:convert'; // Was used for jsonEncode/Decode, ApiClient handles this now for HTTP part
// import 'package:firebase_auth/firebase_auth.dart'; // ApiClient handles auth
// import 'package:http/http.dart' as http; // ApiClient handles HTTP calls

import 'api_client.dart'; // Import the new ApiClient

class IcsValidationResult {
  final bool isValid;
  final String? error;
  final int? nbEvents;

  IcsValidationResult({
    required this.isValid,
    required this.error,
    required this.nbEvents,
  });

  // Optional: Factory constructor for parsing from Map, useful for both paths
  factory IcsValidationResult.fromMap(Map<String, dynamic> data) {
    return IcsValidationResult(
      isValid: data['valid'] ?? false,
      nbEvents: data['nbEvents'] as int?, // Allow null, ensure type safety
      error: data['error'] as String?,   // Allow null
    );
  }
}

abstract class IcsValidationService {
  const IcsValidationService();

  Future<Either<String, IcsValidationResult>> validateUrl(String url);
}

class FirebaseIcsValidationService extends IcsValidationService {
  final FirebaseFunctions functions;
  final ApiClient? apiClient; // New field for ApiClient

  FirebaseIcsValidationService({
    FirebaseFunctions? functions,
    this.apiClient, // New constructor parameter
  }) : functions = functions ?? GetIt.I.get<FirebaseFunctions>();

  @override
  Future<Either<String, IcsValidationResult>> validateUrl(String url) async {
    log('Validating URL: $url');

    if (apiClient != null) {
      log('Using ApiClient for ICS validation');
      try {
        // ApiClient.post is expected to return Map<String, dynamic> on success
        final dynamic responseData = await apiClient!.post(
          'validate-ics-url', // Path should not start with / if ApiClient handles it
          {'url': url},
        );

        if (responseData is Map<String, dynamic>) {
          // Ensure the response is the expected Map before parsing
          final result = IcsValidationResult.fromMap(responseData);
          return right(result);
        } else {
          // This case should ideally be handled by ApiClient returning a typed error or specific exception
          log('ApiClient returned unexpected data type: ${responseData?.runtimeType}');
          return left('API client returned unexpected data type.');
        }
      } on ApiException catch (e) {
        log('ApiException during ICS validation: ${e.message}');
        return left('API Error: ${e.message}'); // Use a more user-friendly prefix or just e.message
      } catch (e) {
        log('Error while validating URL with ApiClient: $e');
        return left('An unexpected error occurred: ${e.toString()}');
      }
    } else {
      log('Using Cloud Function for ICS validation (ApiClient not provided)');
      late HttpsCallableResult cfResponse;
      try {
        cfResponse = await functions.httpsCallable('validate_ics_url').call(
          {'url': url},
        );
      } catch (e) {
        log('Error while validating URL with Cloud Function: $e');
        // Check if e is FirebaseFunctionsException for more specific message
        if (e is FirebaseFunctionsException) {
          return left('Cloud Function Error: ${e.message} (Code: ${e.code})');
        }
        return left('Cloud Function Error: ${e.toString()}');
      }

      log('Validation result from Cloud Function: ${cfResponse.data}');

      try {
        // Ensure cfResponse.data is a Map<String, dynamic> before parsing
        if (cfResponse.data is Map<String, dynamic>) {
           final result = IcsValidationResult.fromMap(cfResponse.data as Map<String, dynamic>);
           return right(result);
        } else {
           log('Cloud Function returned unexpected data type: ${cfResponse.data?.runtimeType}');
           return left('Cloud Function returned unexpected data type.');
        }
      } catch (e) {
        log('Error while parsing Cloud Function validation result: $e');
        return left('Error parsing Cloud Function response: ${e.toString()}');
      }
    }
  }
}

class MockIcsValidationService extends IcsValidationService {
  const MockIcsValidationService();

  @override
  Future<Either<String, IcsValidationResult>> validateUrl(String url) async {
    await Future.delayed(const Duration(milliseconds: 500));
    return right(IcsValidationResult(
      isValid: true,
      error: null,
      nbEvents: 42,
    ));
  }
}
