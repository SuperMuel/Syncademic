import '../models/id.dart';
import '../models/target_calendar.dart';

abstract class TargetCalendarRepository {
  Future<List<TargetCalendar>> getCalendars();
}

class MockTargetCalendarRepository implements TargetCalendarRepository {
  @override
  Future<List<TargetCalendar>> getCalendars() async => List.generate(
      10,
      (index) => TargetCalendar(
          id: ID.fromTrustedSource('target-google-calendar-$index'),
          title: 'Calendar $index'));
}
