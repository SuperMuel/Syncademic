import '../models/id.dart';
import '../models/target_calendar.dart';

abstract class TargetCalendarRepository {
  Future<List<TargetCalendar>> getCalendars(String providerAccountId);

  Future<TargetCalendar> createCalendar(
      String providerAccountId, TargetCalendar calendar);
}

class MockTargetCalendarRepository implements TargetCalendarRepository {
  final List<TargetCalendar> _calendars = List.generate(
    10,
    (index) => TargetCalendar(
      id: ID.fromString('target-google-calendar-$index'),
      title: 'Calendar $index',
      description: 'Description of calendar $index',
      providerAccountId: 'providerAccountId',
    ),
  );

  @override
  Future<List<TargetCalendar>> getCalendars(
    String providerAccountId,
  ) async =>
      _calendars;

  @override
  Future<TargetCalendar> createCalendar(
      String providerAccountId, TargetCalendar calendar) {
    final newCalendar = calendar.copyWith(createdBySyncademic: true);

    _calendars.add(newCalendar);
    return Future.value(newCalendar);
  }
}
