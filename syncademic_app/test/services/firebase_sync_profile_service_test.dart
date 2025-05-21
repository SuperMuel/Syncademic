import 'package:cloud_functions/cloud_functions.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';
import 'package:syncademic_app/models/create_sync_profile_payload.dart'; // For CreateSyncProfileRequest
import 'package:syncademic_app/services/api_client.dart';
import 'package:syncademic_app/services/firebase_sync_profile_service.dart';
import 'package:syncademic_app/services/sync_profile_service.dart'; // For SynchronizationType

// Mocks
class MockApiClient extends Mock implements ApiClient {}
class MockFirebaseFunctions extends Mock implements FirebaseFunctions {}
class MockHttpsCallable extends Mock implements HttpsCallable {}

// Mock for CreateSyncProfileRequest if its methods (like toJson) are complex.
// If toJson is simple, we can instantiate the real object.
// For this case, CreateSyncProfileRequest.toJson() is likely simple, so we'll use the real one.
// If it had complex logic or dependencies, mocking it would be better.
// class MockCreateSyncProfileRequest extends Mock implements CreateSyncProfileRequest {}

@GenerateMocks([MockApiClient, MockFirebaseFunctions, MockHttpsCallable])
void main() {
  late FirebaseSyncProfileService service;
  late MockApiClient mockApiClient;
  late MockFirebaseFunctions mockFirebaseFunctions;
  late MockHttpsCallable mockHttpsCallable;

  const testSyncProfileId = 'test_profile_id';
  const testCalendarUrl = 'https://example.com/calendar.ics';
  const testUserId = 'test_user_id';

  final testRequestPayloadMap = {
    'syncProfileId': testSyncProfileId,
    'syncType': SynchronizationType.regular.name,
  };

  final testCreateRequest = CreateSyncProfileRequest(
    url: testCalendarUrl,
    name: 'Test Calendar',
    userId: testUserId,
    frequencyHours: 2, // Default, doesn't matter for this test
  );
  final testCreatePayloadMap = testCreateRequest.toJson();

  setUp(() {
    mockApiClient = MockApiClient();
    mockFirebaseFunctions = MockFirebaseFunctions();
    mockHttpsCallable = MockHttpsCallable();

    // Default behavior for FirebaseFunctions
    when(mockFirebaseFunctions.httpsCallable(any)).thenReturn(mockHttpsCallable);
  });

  group('FirebaseSyncProfileService', () {
    group('requestSync Method', () {
      group('Cloud Function Path', () {
        setUp(() {
          // Service without ApiClient, or ApiClient flag is false (which is default in service)
          service = FirebaseSyncProfileService(functions: mockFirebaseFunctions);
          when(mockHttpsCallable.call(testRequestPayloadMap)).thenAnswer((_) async {}); // Successful call
        });

        test('should call FirebaseFunctions successfully', () async {
          await expectLater(
            service.requestSync(testSyncProfileId, synchronizationType: SynchronizationType.regular),
            completes,
          );
          verify(mockFirebaseFunctions.httpsCallable('request_sync')).called(1);
          verify(mockHttpsCallable.call(testRequestPayloadMap)).called(1);
          verifyNever(mockApiClient.post(any, any));
        });

        test('should rethrow FirebaseFunctionsException', () async {
          final exception = FirebaseFunctionsException(message: 'Test error', code: 'INTERNAL');
          when(mockHttpsCallable.call(testRequestPayloadMap)).thenThrow(exception);

          await expectLater(
            () => service.requestSync(testSyncProfileId, synchronizationType: SynchronizationType.regular),
            throwsA(isA<FirebaseFunctionsException>()),
          );
          verify(mockFirebaseFunctions.httpsCallable('request_sync')).called(1);
          verify(mockHttpsCallable.call(testRequestPayloadMap)).called(1);
        });
      });

      group('FastAPI Path (currently inactive due to feature flag)', () {
        setUp(() {
          // Service with ApiClient, but feature flag for FastAPI is false in implementation
          service = FirebaseSyncProfileService(
            functions: mockFirebaseFunctions,
            apiClient: mockApiClient,
          );
          when(mockHttpsCallable.call(testRequestPayloadMap)).thenAnswer((_) async {}); // CF success
        });

        test('should still use Cloud Function path when ApiClient is provided but flag is false', () async {
          await expectLater(
            service.requestSync(testSyncProfileId, synchronizationType: SynchronizationType.regular),
            completes,
          );
          verify(mockFirebaseFunctions.httpsCallable('request_sync')).called(1);
          verify(mockHttpsCallable.call(testRequestPayloadMap)).called(1);
          // Verify ApiClient.post was NOT called, as the flag _useFastApiForRequestSync is false
          verifyNever(mockApiClient.post(any, any));
        });

        // TODO: Add tests here when _useFastApiForRequestSync flag can be true
        // test('should call ApiClient.post when flag is true and ApiClient is provided', () async {
        //   // This test would require modifying the service or its flags for testing purposes
        //   // For now, it's a placeholder for future functionality.
        //   when(mockApiClient.post(any, any)).thenAnswer((_) async => {}); // Mock successful API call
        //   // ... (set flag to true, then call, then verify)
        //   expect(true, isFalse, reason: "Test not implemented: FastAPI path for requestSync not active by default");
        // }, skip: true);
      });
    });

    group('createSyncProfile Method', () {
      group('Cloud Function Path', () {
        setUp(() {
          service = FirebaseSyncProfileService(functions: mockFirebaseFunctions);
          when(mockHttpsCallable.call(testCreatePayloadMap)).thenAnswer((_) async {}); // Successful call
        });

        test('should call FirebaseFunctions successfully', () async {
          await expectLater(
            service.createSyncProfile(testCreateRequest),
            completes,
          );
          verify(mockFirebaseFunctions.httpsCallable('create_sync_profile')).called(1);
          verify(mockHttpsCallable.call(testCreatePayloadMap)).called(1);
          verifyNever(mockApiClient.post(any, any));
        });

        test('should rethrow FirebaseFunctionsException', () async {
          final exception = FirebaseFunctionsException(message: 'Test error create', code: 'ABORTED');
          when(mockHttpsCallable.call(testCreatePayloadMap)).thenThrow(exception);

          await expectLater(
            () => service.createSyncProfile(testCreateRequest),
            throwsA(isA<FirebaseFunctionsException>()),
          );
          verify(mockFirebaseFunctions.httpsCallable('create_sync_profile')).called(1);
          verify(mockHttpsCallable.call(testCreatePayloadMap)).called(1);
        });
      });

      group('FastAPI Path (currently inactive due to feature flag)', () {
        setUp(() {
          service = FirebaseSyncProfileService(
            functions: mockFirebaseFunctions,
            apiClient: mockApiClient,
          );
          when(mockHttpsCallable.call(testCreatePayloadMap)).thenAnswer((_) async {}); // CF success
        });

        test('should still use Cloud Function path when ApiClient is provided but flag is false', () async {
          await expectLater(
            service.createSyncProfile(testCreateRequest),
            completes,
          );
          verify(mockFirebaseFunctions.httpsCallable('create_sync_profile')).called(1);
          verify(mockHttpsCallable.call(testCreatePayloadMap)).called(1);
          // Verify ApiClient.post was NOT called, as the flag _useFastApiForCreateProfile is false
          verifyNever(mockApiClient.post(any, any));
        });

        // TODO: Add tests here when _useFastApiForCreateProfile flag can be true
        // test('should call ApiClient.post when flag is true and ApiClient is provided', () async {
        //   // ... (similar to requestSync TODO)
        //   expect(true, isFalse, reason: "Test not implemented: FastAPI path for createSyncProfile not active by default");
        // }, skip: true);
      });
    });
  });
}
