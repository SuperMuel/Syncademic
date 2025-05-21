import 'dart:convert';

import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';
import 'package:syncademic_app/services/api_client.dart';

// Generate mocks for FirebaseAuth, User, and http.Client
// To generate, run: flutter pub run build_runner build
// However, for this environment, we'll define them manually or use simple mock classes.
// For simplicity here, manual mocks using Mockito's `Mock` will be used.

class MockFirebaseAuth extends Mock implements FirebaseAuth {}
class MockUser extends Mock implements User {}
// IdTokenResult is a simple class, usually not needing a full mock for its string token.
// If specific fields of IdTokenResult were needed, then it might be mocked.
// For User.getIdToken(), we usually just care about the returned String or exception.
class MockHttpClient extends Mock implements http.Client {}

@GenerateMocks([MockFirebaseAuth, MockUser, MockHttpClient])
void main() {
  late ApiClient apiClient;
  late MockFirebaseAuth mockFirebaseAuth;
  late MockUser mockUser;
  late MockHttpClient mockHttpClient;

  const String testBaseUrl = 'https://api.example.com';
  const String testToken = 'test_id_token';
  const String testPath = 'test/endpoint';
  final Map<String, dynamic> testBody = {'key': 'value'};
  final String encodedTestBody = jsonEncode(testBody);

  setUp(() {
    mockFirebaseAuth = MockFirebaseAuth();
    mockUser = MockUser();
    mockHttpClient = MockHttpClient();

    // Standard setup: User is logged in and token fetch is successful
    when(mockFirebaseAuth.currentUser).thenReturn(mockUser);
    when(mockUser.getIdToken(true)).thenAnswer((_) async => testToken);

    apiClient = ApiClient(
      baseUrl: testBaseUrl,
      firebaseAuth: mockFirebaseAuth,
      httpClient: mockHttpClient,
    );
  });

  group('ApiClient - Post Method Tests', () {
    group('Successful POST Scenarios', () {
      test('should make a POST request with correct URL, headers, body and return parsed JSON', () async {
        final Map<String, dynamic> mockResponseData = {'status': 'success', 'data': {}};
        final String mockResponseBody = jsonEncode(mockResponseData);
        final expectedUri = Uri.parse('$testBaseUrl/$testPath');
        final expectedHeaders = {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $testToken',
        };

        when(mockHttpClient.post(
          expectedUri,
          headers: expectedHeaders,
          body: encodedTestBody,
        )).thenAnswer((_) async => http.Response(mockResponseBody, 200));

        final result = await apiClient.post(testPath, testBody);

        expect(result, equals(mockResponseData));
        verify(mockHttpClient.post(
          expectedUri,
          headers: expectedHeaders,
          body: encodedTestBody,
        )).called(1);
        verify(mockUser.getIdToken(true)).called(1); // Ensure token was fetched
      });

      test('should return null for successful POST with empty response body', () async {
        final expectedUri = Uri.parse('$testBaseUrl/$testPath');
        when(mockHttpClient.post(
          expectedUri,
          headers: anyNamed('headers'),
          body: anyNamed('body'),
        )).thenAnswer((_) async => http.Response('', 200));

        final result = await apiClient.post(testPath, testBody);

        expect(result, isNull);
      });
    });

    group('Authentication Error Scenarios', () {
      test('should throw ApiException if user is not logged in', () async {
        when(mockFirebaseAuth.currentUser).thenReturn(null);
        // Re-initialize client as auth state is often checked at call time or constructor
        apiClient = ApiClient(
            baseUrl: testBaseUrl,
            firebaseAuth: mockFirebaseAuth,
            httpClient: mockHttpClient);

        expect(
          () async => await apiClient.post(testPath, testBody),
          throwsA(isA<ApiException>().having(
              (e) => e.message, 'message', 'User not authenticated. Cannot get ID token.')),
        );
        verifyNever(mockHttpClient.post(any, headers: anyNamed('headers'), body: anyNamed('body')));
      });

      test('should throw ApiException if ID token fetch fails', () async {
        when(mockUser.getIdToken(true)).thenThrow(FirebaseException(plugin: 'auth', message: 'Token fetch failed'));

        expect(
          () async => await apiClient.post(testPath, testBody),
          throwsA(isA<ApiException>().having(
              (e) => e.message, 'message', contains('Failed to retrieve ID token'))),
        );
        verifyNever(mockHttpClient.post(any, headers: anyNamed('headers'), body: anyNamed('body')));
      });
    });

    group('HTTP Error Scenarios', () {
      test('should throw ApiException for HTTP 400 error with JSON error body', () async {
        final errorResponse = {'detail': 'Bad request'};
        final String errorBody = jsonEncode(errorResponse);
        when(mockHttpClient.post(any, headers: anyNamed('headers'), body: anyNamed('body')))
            .thenAnswer((_) async => http.Response(errorBody, 400));

        expect(
          () async => await apiClient.post(testPath, testBody),
          throwsA(isA<ApiException>()
              .having((e) => e.statusCode, 'statusCode', 400)
              .having((e) => e.message, 'message', 'Bad request')),
        );
      });
       test('should throw ApiException for HTTP 401 error with non-JSON error body', () async {
        const String errorBody = "Unauthorized access";
        when(mockHttpClient.post(any, headers: anyNamed('headers'), body: anyNamed('body')))
            .thenAnswer((_) async => http.Response(errorBody, 401));

        expect(
          () async => await apiClient.post(testPath, testBody),
          throwsA(isA<ApiException>()
              .having((e) => e.statusCode, 'statusCode', 401)
              .having((e) => e.message, 'message', errorBody)),
        );
      });


      test('should throw ApiException for HTTP 500 error', () async {
        when(mockHttpClient.post(any, headers: anyNamed('headers'), body: anyNamed('body')))
            .thenAnswer((_) async => http.Response('Internal server error', 500));

        expect(
          () async => await apiClient.post(testPath, testBody),
          throwsA(isA<ApiException>()
              .having((e) => e.statusCode, 'statusCode', 500)
              .having((e) => e.message, 'message', 'Internal server error')),
        );
      });
    });

    group('Network and Parsing Error Scenarios', () {
      test('should throw ApiException for network error (http.ClientException)', () async {
        final clientException = http.ClientException('Network connection failed');
        when(mockHttpClient.post(any, headers: anyNamed('headers'), body: anyNamed('body')))
            .thenThrow(clientException);

        expect(
          () async => await apiClient.post(testPath, testBody),
          throwsA(isA<ApiException>()
              .having((e) => e.message, 'message', 'Network error: Network connection failed')
              .having((e) => e.originalException, 'originalException', clientException)),
        );
      });

      test('should throw ApiException for JSON parsing error in response', () async {
        const String invalidJsonBody = '{"status": "success", "data": {'; // Malformed JSON
        when(mockHttpClient.post(any, headers: anyNamed('headers'), body: anyNamed('body')))
            .thenAnswer((_) async => http.Response(invalidJsonBody, 200));

        expect(
          () async => await apiClient.post(testPath, testBody),
          throwsA(isA<ApiException>()
              .having((e) => e.statusCode, 'statusCode', 200)
              .having((e) => e.message, 'message', 'Failed to parse JSON response.')
              .having((e) => e.originalException, 'originalException', isA<FormatException>())),
        );
      });
    });

    group('URL Construction Logic', () {
      const pathSegment = 'segment/endpoint';
      test('should correctly join URL: baseUrl with trailing slash, path without leading slash', () async {
        apiClient = ApiClient(baseUrl: '$testBaseUrl/', firebaseAuth: mockFirebaseAuth, httpClient: mockHttpClient);
        final expectedUri = Uri.parse('$testBaseUrl/$pathSegment');
        when(mockHttpClient.post(expectedUri, headers: anyNamed('headers'), body: anyNamed('body')))
            .thenAnswer((_) async => http.Response('{}', 200));
        
        await apiClient.post(pathSegment, testBody);
        verify(mockHttpClient.post(expectedUri, headers: anyNamed('headers'), body: anyNamed('body'))).called(1);
      });

      test('should correctly join URL: baseUrl without trailing slash, path with leading slash', () async {
        apiClient = ApiClient(baseUrl: testBaseUrl, firebaseAuth: mockFirebaseAuth, httpClient: mockHttpClient);
        final expectedUri = Uri.parse('$testBaseUrl/$pathSegment');
         when(mockHttpClient.post(expectedUri, headers: anyNamed('headers'), body: anyNamed('body')))
            .thenAnswer((_) async => http.Response('{}', 200));

        await apiClient.post('/$pathSegment', testBody);
        verify(mockHttpClient.post(expectedUri, headers: anyNamed('headers'), body: anyNamed('body'))).called(1);
      });

      test('should correctly join URL: baseUrl with trailing slash, path with leading slash (double slash avoidance)', () async {
        apiClient = ApiClient(baseUrl: '$testBaseUrl/', firebaseAuth: mockFirebaseAuth, httpClient: mockHttpClient);
        final expectedUri = Uri.parse('$testBaseUrl/$pathSegment'); // ApiClient should handle the double slash
         when(mockHttpClient.post(expectedUri, headers: anyNamed('headers'), body: anyNamed('body')))
            .thenAnswer((_) async => http.Response('{}', 200));

        await apiClient.post('/$pathSegment', testBody);
        verify(mockHttpClient.post(expectedUri, headers: anyNamed('headers'), body: anyNamed('body'))).called(1);
      });
       test('should correctly join URL: baseUrl without trailing slash, path without leading slash', () async {
        apiClient = ApiClient(baseUrl: testBaseUrl, firebaseAuth: mockFirebaseAuth, httpClient: mockHttpClient);
        final expectedUri = Uri.parse('$testBaseUrl/$pathSegment');
         when(mockHttpClient.post(expectedUri, headers: anyNamed('headers'), body: anyNamed('body')))
            .thenAnswer((_) async => http.Response('{}', 200));

        await apiClient.post(pathSegment, testBody);
        verify(mockHttpClient.post(expectedUri, headers: anyNamed('headers'), body: anyNamed('body'))).called(1);
      });
    });
  });
}
