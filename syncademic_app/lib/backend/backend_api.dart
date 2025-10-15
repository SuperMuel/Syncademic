import 'package:cloud_functions/cloud_functions.dart';

/// Defines the contract the app uses to communicate with the backend.
abstract class BackendApi {
  Future<ValidateIcsUrlResponse> validateIcsUrl(String url);
}

/// Response payload returned by `validateIcsUrl`.
class ValidateIcsUrlResponse {
  const ValidateIcsUrlResponse({
    required this.isValid,
    this.error,
    this.nbEvents,
  });

  final bool isValid;
  final String? error;
  final int? nbEvents;

  @override
  String toString() =>
      'ValidateIcsUrlResponse(isValid: $isValid, nbEvents: $nbEvents, error: $error)';
}

/// Base exception thrown when a backend call fails in a controlled way.
class BackendApiException implements Exception {
  BackendApiException(this.message, {this.cause});

  final String message;
  final Object? cause;

  @override
  String toString() => 'BackendApiException: $message';
}

/// Raised when the Firebase Functions client throws a [FirebaseFunctionsException].
class FirebaseBackendApiException extends BackendApiException {
  FirebaseBackendApiException(String message,
      {FirebaseFunctionsException? error})
      : super(message, cause: error);
}

/// Raised when a FastAPI HTTP call fails.
class FastApiBackendException extends BackendApiException {
  FastApiBackendException(String message, {this.statusCode, Object? cause})
      : super(message, cause: cause);

  final int? statusCode;
}
