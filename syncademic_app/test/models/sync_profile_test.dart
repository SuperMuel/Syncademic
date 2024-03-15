import 'package:flutter_test/flutter_test.dart';
import 'package:syncademic_app/models/id.dart';
import 'package:syncademic_app/models/schedule_source.dart';

import 'package:syncademic_app/models/sync_profile.dart';
import 'package:syncademic_app/models/target_calendar.dart';

void main() {
  final id = ID();
  const title = 'Test Title';
  const scheduleSource = ScheduleSource(
    url: 'https://example.com/schedule',
  );

  final targetCalendar = TargetCalendar(
    id: ID(),
    title: 'targetCalendarTitle',
  );

  test('should create a SyncProfile instance', () {
    final syncProfile = SyncProfile(
      id: id,
      title: title,
      scheduleSource: scheduleSource,
      enabled: false,
      targetCalendar: targetCalendar,
    );

    expect(syncProfile.id, id);
    expect(syncProfile.enabled, false);
    expect(syncProfile.scheduleSource, scheduleSource);
    expect(syncProfile.targetCalendar, targetCalendar);
  });

  group('equals', () {
    test('should be equal to another SyncProfile with the same values', () {
      final syncProfile1 = SyncProfile(
        id: id,
        title: title,
        scheduleSource: scheduleSource,
        enabled: false,
        targetCalendar: targetCalendar,
      );
      final syncProfile2 = SyncProfile(
        id: id,
        title: title,
        scheduleSource: scheduleSource,
        enabled: false,
        targetCalendar: targetCalendar,
      );
      expect(syncProfile1, equals(syncProfile2));
    });

    test('should not be equal to another SyncProfile with a different id', () {
      final id1 = ID();
      final syncProfile1 = SyncProfile(
        id: id1,
        title: title,
        scheduleSource: scheduleSource,
        enabled: false,
        targetCalendar: targetCalendar,
      );
      final syncProfile2 = SyncProfile(
        id: id,
        title: title,
        scheduleSource: scheduleSource,
        enabled: false,
        targetCalendar: targetCalendar,
      );
      expect(syncProfile1, isNot(equals(syncProfile2)));
    });

    test('should not be equal to another SyncProfile with a different title',
        () {
      final syncProfile1 = SyncProfile(
        id: id,
        title: title,
        scheduleSource: scheduleSource,
        enabled: false,
        targetCalendar: targetCalendar,
      );
      final syncProfile2 = SyncProfile(
        id: id,
        title: "${title}HHAHAAAAAAAAAAAAAAAAA",
        scheduleSource: scheduleSource,
        enabled: false,
        targetCalendar: targetCalendar,
      );
      expect(syncProfile1, isNot(equals(syncProfile2)));
    });

    test(
        'should not be equal to another SyncProfile with a different scheduleSource',
        () {
      final scheduleSource1 = scheduleSource.copyWith(
        url: 'https://example.com/schedule1',
      );
      final syncProfile1 = SyncProfile(
        id: id,
        title: title,
        scheduleSource: scheduleSource1,
        enabled: false,
        targetCalendar: targetCalendar,
      );
      final syncProfile2 = SyncProfile(
        id: id,
        title: title,
        scheduleSource: scheduleSource,
        enabled: false,
        targetCalendar: targetCalendar,
      );
      expect(syncProfile1, isNot(equals(syncProfile2)));
    });

    test(
        'should not be equal to another SyncProfile with a different targetCalendar',
        () {
      final targetCalendar1 = targetCalendar.copyWith(
        title: 'Test Title 1',
      );

      final syncProfile1 = SyncProfile(
        id: id,
        title: title,
        scheduleSource: scheduleSource,
        enabled: false,
        targetCalendar: targetCalendar1,
      );
      final syncProfile2 = SyncProfile(
        id: id,
        title: title,
        scheduleSource: scheduleSource,
        enabled: false,
        targetCalendar: targetCalendar,
      );
      expect(syncProfile1, isNot(equals(syncProfile2)));
    });

    test('should not be equal to another SyncProfile with a different enabled',
        () {
      final syncProfile1 = SyncProfile(
        id: id,
        title: title,
        scheduleSource: scheduleSource,
        enabled: true,
        targetCalendar: targetCalendar,
      );
      final syncProfile2 = SyncProfile(
        id: id,
        title: title,
        scheduleSource: scheduleSource,
        enabled: false,
        targetCalendar: targetCalendar,
      );
      expect(syncProfile1, isNot(equals(syncProfile2)));
    });

    test('should have the same hash code for SyncProfiles with the same values',
        () {
      final syncProfile1 = SyncProfile(
        id: id,
        title: title,
        scheduleSource: scheduleSource,
        enabled: false,
        targetCalendar: targetCalendar,
      );
      final syncProfile2 = SyncProfile(
        id: id,
        title: title,
        scheduleSource: scheduleSource,
        enabled: false,
        targetCalendar: targetCalendar,
      );
      expect(syncProfile1.hashCode, equals(syncProfile2.hashCode));
    });
  });
}
