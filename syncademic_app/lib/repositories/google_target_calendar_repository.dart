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

    final result = await FirebaseFunctions.instance
        .httpsCallable('list_user_calendars')
        .call({'providerAccountId': providerAccountId});

    final calendars = result.data['calendars'] as List<dynamic>;

    return calendars
        .map((calendar) => TargetCalendar(
              id: ID.fromString(calendar['id']),
              title: calendar['summary'] ?? 'Unnamed calendar',
              description: calendar['description'],
              providerAccountId: providerAccountId,
            ))
        .toList();
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
    final result = await FirebaseFunctions.instance
        .httpsCallable('create_new_calendar')
        .call({
      'providerAccountId': await _getProviderAccountId(),
      'summary': targetCalendar.title,
      'description': targetCalendar.description,
    });

    return targetCalendar.copyWith(
      id: ID.fromString(result.data['id'] as String),
      createdBySyncademic: true,
    );
  }
}
