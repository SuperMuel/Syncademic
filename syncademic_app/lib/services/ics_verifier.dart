import 'package:http/http.dart' as http;
import 'package:fpdart/fpdart.dart';

class IcsValidationService {
  const IcsValidationService();

  bool isIcsContentValid(String content) =>
      content.contains('BEGIN:VCALENDAR') && content.contains('END:VCALENDAR');

  Future<Either<String, String>> fetchAndParseIcs(String url) async {
    try {
      final response = await http.get(Uri.parse(url));

      if (response.statusCode != 200) {
        return Left(
            'Failed to fetch data. Status code: ${response.statusCode}');
      }

      final content = response.body;

      return Either<String, String>.fromPredicate(
          content, isIcsContentValid, (_) => "Invalid ICS content.");
    } catch (e) {
      return Left(e.toString());
    }
  }
}
