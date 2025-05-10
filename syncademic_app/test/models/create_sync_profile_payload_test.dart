import 'package:flutter_test/flutter_test.dart';
import 'package:syncademic_app/models/create_sync_profile_payload.dart';
import 'package:syncademic_app/models/schedule_source.dart';

void main() {
  group('CreateSyncProfileRequest', () {
    test('toJson returns correct map for createNew targetCalendar', () {
      const payload = CreateSyncProfileRequest(
        title: 'Test Profile',
        scheduleSource: ScheduleSource(url: 'https://example.com/ics'),
        targetCalendar: TargetCalendarPayload.createNew(
          providerAccountId: 'provider-123',
          colorId: '5',
        ),
      );

      final json = payload.toJson();
      expect({
        'title': json['title'],
        'scheduleSource': {'url': 'https://example.com/ics'},
        'targetCalendar': {
          'type': 'createNew',
          'providerAccountId': 'provider-123',
          'colorId': '5',
        },
      }, {
        'title': 'Test Profile',
        'scheduleSource': {'url': 'https://example.com/ics'},
        'targetCalendar': {
          'type': 'createNew',
          'providerAccountId': 'provider-123',
          'colorId': '5',
        },
      });
    });
  });

  group('TargetCalendarPayload', () {
    test('toJson returns correct map for createNew', () {
      const payload = TargetCalendarPayload.createNew(
        providerAccountId: 'provider-123',
        colorId: '5',
      );
      expect(payload.toJson(), {
        'type': 'createNew',
        'providerAccountId': 'provider-123',
        'colorId': '5',
      });
    });

    test('toJson returns correct map for useExisting', () {
      const payload = TargetCalendarPayload.useExisting(
        providerAccountId: 'provider-456',
        calendarId: 'calendar-789',
      );
      expect(payload.toJson(), {
        'type': 'useExisting',
        'providerAccountId': 'provider-456',
        'calendarId': 'calendar-789',
      });
    });

    test('fromJson creates correct createNew instance', () {
      final json = {
        'type': 'createNew',
        'providerAccountId': 'provider-123',
        'colorId': '5',
      };
      final payload = TargetCalendarPayload.fromJson(json);
      expect(payload, isA<CreateNewTargetCalendarPayload>());
      expect((payload as CreateNewTargetCalendarPayload).providerAccountId,
          'provider-123');
      expect(payload.colorId, '5');
    });

    test('fromJson creates correct useExisting instance', () {
      final json = {
        'type': 'useExisting',
        'providerAccountId': 'provider-456',
        'calendarId': 'calendar-789',
      };
      final payload = TargetCalendarPayload.fromJson(json);
      expect(payload, isA<UseExistingTargetCalendarPayload>());
      expect((payload as UseExistingTargetCalendarPayload).providerAccountId,
          'provider-456');
      expect(payload.calendarId, 'calendar-789');
    });
  });
}
