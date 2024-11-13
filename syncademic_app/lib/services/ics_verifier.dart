import 'package:http/http.dart' as http;
import 'package:fpdart/fpdart.dart';

class Failure {
  final String message;
  Failure(this.message);
}

class Success {
  final String content;
  Success(this.content);
}

class IcsValidationService {
  const IcsValidationService();

  Future<Either<Failure, Success>> fetchAndParseIcs(String url) async {
    try {
      final response = await http.get(Uri.parse(url));

      if (response.statusCode == 200) {
        final content = response.body;

        // Perform basic validation to check if it's a valid ICS content
        if (content.contains('BEGIN:VCALENDAR') &&
            content.contains('END:VCALENDAR')) {
          return Right(Success(content));
        } else {
          return Left(Failure('Invalid ICS content.'));
        }
      } else {
        return Left(Failure(
            'Failed to fetch data. Status code: ${response.statusCode}'));
      }
    } catch (e) {
      return Left(Failure('An error occurred: $e'));
    }
  }
}
