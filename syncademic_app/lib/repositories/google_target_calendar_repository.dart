import 'package:googleapis/calendar/v3.dart';
import 'package:http/http.dart' as http;

import '../models/id.dart';
import '../models/target_calendar.dart';
import 'target_calendar_repository.dart';

// TODO : All the google calendars are not yet target calendars. Those are just
// Google calendars ! We need to rename this class to GoogleCalendarRepository
// and TargetCalendarRepository to GoogleTargetCalendarRepository
// and make them return Calendar instead of TargetCalendar
// and handle access token elsewhere

class GoogleTargetCalendarRepository implements TargetCalendarRepository {
  final CalendarApi _client;
  final String? accessToken;

  GoogleTargetCalendarRepository(
      {required http.Client authorizedClient, this.accessToken})
      : _client = CalendarApi(authorizedClient);

  @override
  Future<List<TargetCalendar>> getCalendars() async {
    final calendarList = await _client.calendarList.list();
    return calendarList.items!
        .map((calendarListEntry) => TargetCalendar(
              id: ID.fromString(calendarListEntry.id!),
              title: calendarListEntry.summary!,
              accessToken: accessToken,
            ))
        .toList();
  }
}
