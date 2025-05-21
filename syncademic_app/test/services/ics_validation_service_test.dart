import 'package:cloud_functions/cloud_functions.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:fpdart/fpdart.dart';
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';
import 'package:syncademic_app/services/api_client.dart';
import 'package:syncademic_app/services/ics_validation_service.dart';

// Mocks - If using build_runner, these would be in a .mocks.dart file
// For simplicity, defining minimal mock classes or using Mockito's Mock directly.
class MockApiClient extends Mock implements ApiClient {}
class MockFirebaseFunctions extends Mock implements FirebaseFunctions {}
class MockHttpsCallable extends Mock implements HttpsCallable {}
class MockHttpsCallableResult extends Mock implements HttpsCallableResult {}
// MockUser and MockFirebaseAuth are not directly needed here anymore as ApiClient handles its own auth
// and FirebaseFunctions mocking doesn't require user details for these tests.

@GenerateMocks([MockApiClient, MockFirebaseFunctions, MockHttpsCallable, MockHttpsCallableResult])
void main() {
  late FirebaseIcsValidationService service;
  late MockApiClient mockApiClient;
  late MockFirebaseFunctions mockFirebaseFunctions;
  late MockHttpsCallable mockHttpsCallable;
  late MockHttpsCallableResult mockHttpsCallableResult;

  const testUrl = 'https://example.com/calendar.ics';
  final Map<String, String> expectedCloudFunctionArgs = {'url': testUrl};
  const String validateIcsUrlPath = 'validate-ics-url';

  setUp(() {
    mockApiClient = MockApiClient();
    mockFirebaseFunctions = MockFirebaseFunctions();
    mockHttpsCallable = MockHttpsCallable();
    mockHttpsCallableResult = MockHttpsCallableResult();

    // Default behavior for FirebaseFunctions
    when(mockFirebaseFunctions.httpsCallable(any)).thenReturn(mockHttpsCallable);
    when(mockHttpsCallable.call(any)).thenAnswer((_) async => mockHttpsCallableResult);
  });

  group('FirebaseIcsValidationService - validateUrl', () {
    group('ApiClient Path (ApiClient is provided)', () {
      setUp(() {
        service = FirebaseIcsValidationService(
          functions: mockFirebaseFunctions, // Still needed for constructor
          apiClient: mockApiClient, // Key for this path
        );
      });

      test('should return Right(IcsValidationResult) for valid ICS from ApiClient', () async {
        final successResponse = {'valid': true, 'nbEvents': 15, 'error': null};
        when(mockApiClient.post(validateIcsUrlPath, {'url': testUrl}))
            .thenAnswer((_) async => successResponse);

        final result = await service.validateUrl(testUrl);

        expect(result.isRight(), isTrue);
        result.fold(
          (l) => fail('Expected Right, got Left: $l'),
          (r) {
            expect(r.isValid, isTrue);
            expect(r.nbEvents, 15);
            expect(r.error, isNull);
          },
        );
        verify(mockApiClient.post(validateIcsUrlPath, {'url': testUrl})).called(1);
        verifyNever(mockFirebaseFunctions.httpsCallable(any)); // Ensure Cloud Function not called
      });

      test('should return Right(IcsValidationResult) for invalid ICS from ApiClient', () async {
        final invalidResponse = {'valid': false, 'nbEvents': 0, 'error': 'Invalid calendar format'};
        when(mockApiClient.post(validateIcsUrlPath, {'url': testUrl}))
            .thenAnswer((_) async => invalidResponse);

        final result = await service.validateUrl(testUrl);

        expect(result.isRight(), isTrue);
        result.fold(
          (l) => fail('Expected Right, got Left: $l'),
          (r) {
            expect(r.isValid, isFalse);
            expect(r.nbEvents, 0);
            expect(r.error, 'Invalid calendar format');
          },
        );
        verify(mockApiClient.post(validateIcsUrlPath, {'url': testUrl})).called(1);
      });

      test('should return Left(errorMessage) when ApiClient throws ApiException', () async {
        final apiException = ApiException(message: 'Network Error', statusCode: 503);
        when(mockApiClient.post(validateIcsUrlPath, {'url': testUrl}))
            .thenThrow(apiException);

        final result = await service.validateUrl(testUrl);

        expect(result.isLeft(), isTrue);
        result.fold(
          (l) => expect(l, 'API Error: Network Error'),
          (r) => fail('Expected Left, got Right: $r'),
        );
        verify(mockApiClient.post(validateIcsUrlPath, {'url': testUrl})).called(1);
      });

      test('should return Left(errorMessage) for unexpected data type from ApiClient', () async {
        // Scenario where ApiClient.post returns something other than Map<String, dynamic>
        when(mockApiClient.post(validateIcsUrlPath, {'url': testUrl}))
            .thenAnswer((_) async => "This is not a map"); // e.g. String

        final result = await service.validateUrl(testUrl);

        expect(result.isLeft(), isTrue);
        result.fold(
          (l) => expect(l, 'API client returned unexpected data type.'),
          (r) => fail('Expected Left, got Right: $r'),
        );
        verify(mockApiClient.post(validateIcsUrlPath, {'url': testUrl})).called(1);
      });
    });

    group('Cloud Function Path (ApiClient is null)', () {
      setUp(() {
        service = FirebaseIcsValidationService(
          functions: mockFirebaseFunctions,
          apiClient: null, // Key for this path
        );
      });

      test('should return Right(IcsValidationResult) for successful Cloud Function call', () async {
        final successData = {'valid': true, 'nbEvents': 5, 'error': null};
        when(mockHttpsCallableResult.data).thenReturn(successData);
        when(mockHttpsCallable.call(expectedCloudFunctionArgs)).thenAnswer((_) async => mockHttpsCallableResult);


        final result = await service.validateUrl(testUrl);

        expect(result.isRight(), isTrue);
        result.fold(
          (l) => fail('Expected Right, got Left: $l'),
          (r) {
            expect(r.isValid, isTrue);
            expect(r.nbEvents, 5);
            expect(r.error, isNull);
          },
        );
        verify(mockFirebaseFunctions.httpsCallable('validate_ics_url')).called(1);
        verify(mockHttpsCallable.call(expectedCloudFunctionArgs)).called(1);
        verifyNever(mockApiClient.post(any, any)); // Ensure ApiClient not called
      });

      test('should return Left(errorMessage) when Cloud Function throws FirebaseFunctionsException', () async {
        final exception = FirebaseFunctionsException(message: 'Internal error', code: 'INTERNAL');
        when(mockHttpsCallable.call(expectedCloudFunctionArgs)).thenThrow(exception);

        final result = await service.validateUrl(testUrl);

        expect(result.isLeft(), isTrue);
        result.fold(
          (l) => expect(l, 'Cloud Function Error: Internal error (Code: INTERNAL)'),
          (r) => fail('Expected Left, got Right: $r'),
        );
        verify(mockFirebaseFunctions.httpsCallable('validate_ics_url')).called(1);
        verify(mockHttpsCallable.call(expectedCloudFunctionArgs)).called(1);
      });

      test('should return Left(errorMessage) for unexpected data type from Cloud Function', () async {
        when(mockHttpsCallableResult.data).thenReturn("Not a map"); // e.g. String
        when(mockHttpsCallable.call(expectedCloudFunctionArgs)).thenAnswer((_) async => mockHttpsCallableResult);

        final result = await service.validateUrl(testUrl);

        expect(result.isLeft(), isTrue);
        result.fold(
          (l) => expect(l, 'Cloud Function returned unexpected data type.'),
          (r) => fail('Expected Left, got Right: $r'),
        );
      });
    });
  });
}
