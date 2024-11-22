import 'package:cloud_functions/cloud_functions.dart';
import '../models/id.dart';
import '../models/target_calendar.dart';
import 'target_calendar_repository.dart';

class GoogleTargetCalendarRepository implements TargetCalendarRepository {
  GoogleTargetCalendarRepository();

  @override
  Future<List<TargetCalendar>> getCalendars(
    {required String providerAccountId, required String providerAccountEmail}
  ) async {
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
              providerAccountEmail: providerAccountEmail,
            ))
        .toList();
  }

  @override
  Future<TargetCalendar> createCalendar(
      String providerAccountId, TargetCalendar targetCalendar,
      {GoogleCalendarColor? color}) async {
    final result = await FirebaseFunctions.instance
        .httpsCallable('create_new_calendar')
        .call({
      'providerAccountId': providerAccountId,
      'providerAccountEmail': targetCalendar.providerAccountEmail,
      'summary': targetCalendar.title,
      'description': targetCalendar.description,
      'colorId': color == null ? null : int.parse(color.id),
    });

    return targetCalendar.copyWith(
      id: ID.fromString(result.data['id'] as String),
      createdBySyncademic: true,
      providerAccountId: providerAccountId,
    );
  }
}
