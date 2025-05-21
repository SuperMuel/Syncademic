import 'dart:async';
import 'dart:convert';
import 'dart:io'; // For HttpStatus

import 'package:firebase_auth/firebase_auth.dart';
import 'package:http/http.dart' as http;

// Custom Exception for API related errors
class ApiException implements Exception {
  final int? statusCode;
  final String message;
  final dynamic originalException;

  ApiException({
    this.statusCode,
    required this.message,
    this.originalException,
  });

  @override
  String toString() {
    return 'ApiException: $message (Status Code: $statusCode, Original Exception: $originalException)';
  }
}

class ApiClient {
  final String baseUrl;
  final FirebaseAuth _firebaseAuth;
  final http.Client _httpClient; // Allow injecting for testability

  ApiClient({
    required this.baseUrl,
    FirebaseAuth? firebaseAuth,
    http.Client? httpClient, // Optional for testing
  })  : _firebaseAuth = firebaseAuth ?? FirebaseAuth.instance,
        _httpClient = httpClient ?? http.Client();

  Future<String> _getIdToken() async {
    final currentUser = _firebaseAuth.currentUser;
    if (currentUser == null) {
      throw StateError('User not authenticated. Cannot get ID token.');
    }
    try {
      return await currentUser.getIdToken(true); // Force refresh
    } catch (e) {
      throw StateError('Failed to retrieve ID token: ${e.toString()}');
    }
  }

  Future<dynamic> post(String path, Map<String, dynamic> body) async {
    // Ensure path doesn't start with '/' if baseUrl already ends with one,
    // or that path starts with '/' if baseUrl doesn't.
    // A common way is to ensure baseUrl does not have a trailing slash,
    // and path always starts with one, or use Uri.resolve for robustness.
    final String cleanPath = path.startsWith('/') ? path.substring(1) : path;
    final String cleanBaseUrl = baseUrl.endsWith('/') ? baseUrl.substring(0, baseUrl.length -1) : baseUrl;
    final Uri url = Uri.parse('$cleanBaseUrl/$cleanPath');

    String idToken;
    try {
      idToken = await _getIdToken();
    } on StateError catch (e) {
      // This indicates an authentication issue before even making a call
      throw ApiException(message: e.message, originalException: e);
    }

    final headers = {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $idToken',
    };

    final encodedBody = jsonEncode(body);

    try {
      final response = await _httpClient.post(
        url,
        headers: headers,
        body: encodedBody,
      );

      // Check for common success codes (200-299)
      if (response.statusCode >= 200 && response.statusCode < 300) {
        if (response.body.isEmpty) {
          return null; // Or an empty map: {}
        }
        // Attempt to parse JSON, handle if it's not JSON or empty
        try {
          return jsonDecode(response.body);
        } catch (e) {
          throw ApiException(
            statusCode: response.statusCode,
            message: 'Failed to parse JSON response.',
            originalException: e,
          );
        }
      } else {
        // Handle HTTP errors
        String errorMessage = 'API request failed';
        try {
          // Try to get more specific error from response body if it's JSON
          final errorBody = jsonDecode(response.body);
          if (errorBody is Map && errorBody.containsKey('detail')) {
            errorMessage = errorBody['detail'];
          } else if (errorBody is Map && errorBody.containsKey('message')) {
             errorMessage = errorBody['message'];
          } else {
            errorMessage = response.body;
          }
        } catch (_) {
          // If response body is not JSON or not in expected format
          errorMessage = response.body.isNotEmpty ? response.body : 'HTTP Error ${response.statusCode}';
        }
        throw ApiException(
          statusCode: response.statusCode,
          message: errorMessage,
        );
      }
    } on http.ClientException catch (e) {
      // Network errors (socket exception, dns lookup, etc.)
      throw ApiException(message: 'Network error: ${e.message}', originalException: e);
    } on TimeoutException catch (e) {
      throw ApiException(message: 'Request timed out: ${e.message}', originalException: e);
    } catch (e) {
      // Catch-all for other unexpected errors
      throw ApiException(message: 'An unexpected error occurred: ${e.toString()}', originalException: e);
    }
  }

  // Example for a GET request, can be added later if needed
  // Future<dynamic> get(String path) async { ... }

  // Dispose method to close the client if it's owned by this ApiClient instance
  void dispose() {
    // Only close the client if it was created by this class (not injected)
    // This is a bit tricky to manage without knowing who owns the client.
    // If a new http.Client() is created in the constructor (when httpClient is null), then it should be closed.
    // For simplicity, if _httpClient is just http.Client(), it can be closed.
    // However, the default http.Client() is a singleton-like instance and closing it might affect other parts of the app.
    // It's generally better if the creator of the client is responsible for closing it.
    // If using a fresh http.Client() instance per ApiClient, then:
    // _httpClient.close();
  }
}
