import 'dart:convert';

import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:get_it/get_it.dart';
import 'package:http/http.dart' as http;

import '../services/auth_service.dart';
import 'backend_api.dart';

class FastApiBackendApi implements BackendApi {
  FastApiBackendApi({
    http.Client? httpClient,
    AuthService? authService,
    String? baseUrl,
  })  : _client = httpClient ?? http.Client(),
        _authService = authService ?? GetIt.I<AuthService>(),
        _baseUri = _parseBaseUrl(baseUrl ?? dotenv.env['FASTAPI_BASE_URL']);

  final http.Client _client;
  final AuthService _authService;
  final Uri _baseUri;

  static Uri _parseBaseUrl(String? rawUrl) {
    if (rawUrl == null) {
      throw FastApiBackendException(
        'FASTAPI_BASE_URL is not defined. Set it in dotenv to use the FastAPI backend.',
      );
    }

    final trimmed = rawUrl.trim();
    if (trimmed.isEmpty) {
      throw FastApiBackendException(
        'FASTAPI_BASE_URL is empty. Provide a valid FastAPI server URL.',
      );
    }

    try {
      final uri = Uri.parse(trimmed);
      if (!uri.hasScheme) {
        throw FastApiBackendException(
          'FASTAPI_BASE_URL "$trimmed" is missing a scheme. Include http:// or https://.',
        );
      }
      if (!uri.hasAuthority) {
        throw FastApiBackendException(
          'FASTAPI_BASE_URL "$trimmed" is missing a host. Expected something like http://127.0.0.1:8000.',
        );
      }
      return uri;
    } on FormatException catch (e) {
      throw FastApiBackendException(
        'Could not parse FASTAPI_BASE_URL "$trimmed": ${e.message}.',
      );
    }
  }

  Uri _buildUri(String path) => _baseUri.resolve(path);

  @override
  Future<ValidateIcsUrlResponse> validateIcsUrl(String url) async {
    final token = await _authService.getIdToken();
    if (token == null) {
      throw FastApiBackendException(
        'Unable to call FastAPI: Firebase ID token is null.',
      );
    }

    final requestUri = _buildUri('/ics/validate');
    try {
      final response = await _client.post(
        requestUri,
        headers: <String, String>{
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: jsonEncode(<String, dynamic>{'url': url}),
      );

      if (response.statusCode < 200 || response.statusCode >= 300) {
        throw FastApiBackendException(
          'FastAPI validate_ics_url failed with status ${response.statusCode}. Body: ${response.body}',
          statusCode: response.statusCode,
        );
      }

      final decoded = jsonDecode(response.body);
      if (decoded is! Map<String, dynamic>) {
        throw FastApiBackendException(
          'FastAPI validate_ics_url returned unexpected payload: ${response.body}',
          statusCode: response.statusCode,
        );
      }

      return ValidateIcsUrlResponse(
        isValid: decoded['valid'] as bool? ?? false,
        nbEvents: decoded['nbEvents'] is num
            ? (decoded['nbEvents'] as num).toInt()
            : decoded['nbEvents'] as int?,
        error: decoded['error'] as String?,
      );
    } catch (e) {
      if (e is FastApiBackendException) {
        rethrow;
      }
      throw FastApiBackendException('FastAPI request failed: $e');
    }
  }
}
