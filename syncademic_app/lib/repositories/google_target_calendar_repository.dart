import 'package:googleapis/calendar/v3.dart';
import '../models/id.dart';
import '../models/target_calendar.dart';
import 'target_calendar_repository.dart';
import 'package:http/http.dart' as http;

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
              id: ID.fromTrustedSource(calendarListEntry.id!),
              title: calendarListEntry.summary!,
              accessToken: accessToken,
            ))
        .toList();
  }
}
