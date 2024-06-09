import 'package:cloud_functions/cloud_functions.dart';
import 'package:get_it/get_it.dart';
import 'package:googleapis/calendar/v3.dart';

import '../authorization/authorization_service.dart';
import '../models/id.dart';
import '../models/target_calendar.dart';
import 'target_calendar_repository.dart';

// TODO : All the google calendars are not yet target calendars. Those are just
// Google calendars ! We need to rename this class to GoogleCalendarRepository
// and TargetCalendarRepository to GoogleTargetCalendarRepository
// and make them return Calendar instead of TargetCalendar
// and handle access token elsewhere

class GoogleTargetCalendarRepository implements TargetCalendarRepository {
  GoogleTargetCalendarRepository();

  @override
  Future<List<TargetCalendar>> getCalendars() async {
    String? providerAccountId = await _getProviderAccountId();

    // find cloud function to get calendars

    final result = await FirebaseFunctions.instance
        .httpsCallable('list_user_calendars')
        .call<Map<String, dynamic>>({
      'providerAccountId': providerAccountId,
    });

    final calendars = result.data['calendars'] as List<Map<String, dynamic>>;

    return calendars
        .map((calendar) => TargetCalendar(
              id: ID.fromString(calendar['id']),
              title: calendar['summary'] ?? 'Unnamed calendar',
              description: calendar['description'],
              providerAccountId: providerAccountId,
            ))
        .toList();
  }

  Future<CalendarApi> _getApi() async {
    final authorizedClient =
        await GetIt.I<AuthorizationService>().authorizedClient;

    if (authorizedClient == null) {
      throw Exception(
          "Could not get an authorized client from the AuthorizationService");
    }

    return CalendarApi(authorizedClient);
  }

  Future<String> _getProviderAccountId() async {
    final providerAccountId = await GetIt.I<AuthorizationService>().userId;
    if (providerAccountId == null) {
      throw Exception(
          "Could not get the user ID from the AuthorizationService");
    }
    return providerAccountId;
  }

  @override
  Future<TargetCalendar> createCalendar(TargetCalendar targetCalendar) async {
    final api = await _getApi();

    //TODO : handle timezone information
    final calendar = Calendar(
      summary: targetCalendar.title,
      description: targetCalendar.description,
    );

    final createdCalendar = await api.calendars.insert(calendar);

    if (createdCalendar.id == null) {
      throw Exception("Created calendar ID is null");
    }

    return targetCalendar.copyWith(
      id: ID.fromString(createdCalendar.id!),
      createdBySyncademic: true,
    );
  }
}
