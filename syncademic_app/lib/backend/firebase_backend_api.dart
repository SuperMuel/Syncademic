import 'package:cloud_functions/cloud_functions.dart';
import 'package:get_it/get_it.dart';

import 'backend_api.dart';

class FirebaseBackendApi implements BackendApi {
  FirebaseBackendApi({FirebaseFunctions? functions})
      : _functions = functions ?? GetIt.I<FirebaseFunctions>();

  final FirebaseFunctions _functions;

  @override
  Future<ValidateIcsUrlResponse> validateIcsUrl(String url) async {
    try {
      final result = await _functions
          .httpsCallable('validate_ics_url')
          .call(<String, dynamic>{'url': url});

      final rawData = result.data;
      if (rawData is! Map) {
        throw BackendApiException(
          'Unexpected Firebase response type for validate_ics_url: ${rawData.runtimeType}',
        );
      }

      final data = Map<String, dynamic>.from(
        rawData as Map<dynamic, dynamic>,
      );
      return ValidateIcsUrlResponse(
        isValid: data['valid'] as bool? ?? false,
        nbEvents: data['nbEvents'] is num
            ? (data['nbEvents'] as num).toInt()
            : data['nbEvents'] as int?,
        error: data['error'] as String?,
      );
    } on FirebaseFunctionsException catch (e) {
      throw FirebaseBackendApiException(
        'Firebase validate_ics_url failed: ${e.code}',
        error: e,
      );
    } catch (e) {
      throw BackendApiException('Unexpected Firebase backend error: $e',
          cause: e);
    }
  }
}
