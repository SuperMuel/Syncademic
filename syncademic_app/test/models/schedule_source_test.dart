import 'package:flutter_test/flutter_test.dart';
import 'package:syncademic_app/models/schedule_source.dart';

void main() {
  {
    test('should have correct url when created using the constructor', () {
      const url = 'https://example.com/schedule';
      const scheduleSource = ScheduleSource(url: url);
      expect(scheduleSource.url, equals(url));
    });

    group('equals', () {
      test('should be equal to another ScheduleSource with the same url', () {
        const url = 'https://example.com/schedule';
        const scheduleSource1 = ScheduleSource(url: url);
        const scheduleSource2 = ScheduleSource(url: url);
        expect(scheduleSource1, equals(scheduleSource2));
      });

      test('should not be equal to another ScheduleSource with a different url',
          () {
        const url1 = 'https://example.com/schedule1';
        const url2 = 'https://example.com/schedule2';
        const scheduleSource1 = ScheduleSource(url: url1);
        const scheduleSource2 = ScheduleSource(url: url2);
        expect(scheduleSource1, isNot(equals(scheduleSource2)));
      });

      test(
          'should have the same hash code for ScheduleSources with the same url',
          () {
        const url = 'https://example.com/schedule';
        const scheduleSource1 = ScheduleSource(url: url);
        const scheduleSource2 = ScheduleSource(url: url);
        expect(scheduleSource1.hashCode, equals(scheduleSource2.hashCode));
      });

      test(
          'should have different hash codes for ScheduleSources with different urls',
          () {
        const url1 = 'https://example.com/schedule1';
        const url2 = 'https://example.com/schedule2';
        const scheduleSource1 = ScheduleSource(url: url1);
        const scheduleSource2 = ScheduleSource(url: url2);
        expect(
            scheduleSource1.hashCode, isNot(equals(scheduleSource2.hashCode)));
      });
    });
  }
}
