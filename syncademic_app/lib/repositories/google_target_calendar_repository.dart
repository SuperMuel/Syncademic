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
    final api = await _getApi();

    String? accountOwnerUserId = await _getAccountOwnerUserId();

    final calendarList = await api.calendarList.list();
    return calendarList.items!
        .map((calendarListEntry) => TargetCalendar(
              id: ID.fromString(calendarListEntry.id!),
              title: calendarListEntry.summary ?? 'Unnamed calendar',
              accountOwnerUserId: accountOwnerUserId,
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

  Future<String> _getAccountOwnerUserId() async {
    final accountOwnerUserId = await GetIt.I<AuthorizationService>().userId;
    if (accountOwnerUserId == null) {
      throw Exception(
          "Could not get the user ID from the AuthorizationService");
    }
    return accountOwnerUserId;
  }
}
