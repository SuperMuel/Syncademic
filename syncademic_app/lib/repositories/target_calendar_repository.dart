import '../models/id.dart';
import '../models/target_calendar.dart';

abstract class TargetCalendarRepository {
  Future<List<TargetCalendar>> getCalendars();

  Future<TargetCalendar> createCalendar(TargetCalendar calendar);
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
  Future<List<TargetCalendar>> getCalendars() async => _calendars;

  @override
  Future<TargetCalendar> createCalendar(TargetCalendar calendar) {
    final _calendar = calendar.copyWith(createdBySyncademic: true);

    _calendars.add(_calendar);
    return Future.value(_calendar);
  }
}
