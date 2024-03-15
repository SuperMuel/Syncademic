import 'package:flutter_test/flutter_test.dart';
import 'package:syncademic_app/models/id.dart';
import 'package:syncademic_app/models/target_calendar.dart';

void main() {
  const id = ID.fromTrustedSource('test_id');
  const title = 'Test Title';
  const accessToken = 'test_access_token';

  test('should create a TargetCalendar instance', () {
    const targetCalendar = TargetCalendar(
      id: id,
      title: title,
      accessToken: accessToken,
    );

    expect(targetCalendar.id, id);
    expect(targetCalendar.title, title);
    expect(targetCalendar.accessToken, accessToken);
  });

  group('equals', () {
    test('should be equal to another TargetCalendar with the values', () {
      const targetCalendar1 = TargetCalendar(
        id: id,
        title: title,
        accessToken: accessToken,
      );
      const targetCalendar2 = TargetCalendar(
        id: id,
        title: title,
        accessToken: accessToken,
      );
      expect(targetCalendar1, equals(targetCalendar2));
    });

    test('should not be equal to another TargetCalendar with a different id',
        () {
      const id1 = ID.fromTrustedSource('test_id1');
      const targetCalendar1 = TargetCalendar(
        id: id1,
        title: title,
        accessToken: accessToken,
      );
      const targetCalendar2 = TargetCalendar(
        id: id,
        title: title,
        accessToken: accessToken,
      );
      expect(targetCalendar1, isNot(equals(targetCalendar2)));
    });

    test('should not be equal to another TargetCalendar with a different title',
        () {
      const title1 = 'Test Title 1';
      const targetCalendar1 = TargetCalendar(
        id: id,
        title: title1,
        accessToken: accessToken,
      );
      const targetCalendar2 = TargetCalendar(
        id: id,
        title: title,
        accessToken: accessToken,
      );
      expect(targetCalendar1, isNot(equals(targetCalendar2)));
    });

    test(
        'should not be equal to another TargetCalendar with a different accessToken',
        () {
      const accessToken1 = 'test_access_token1';
      const targetCalendar1 = TargetCalendar(
        id: id,
        title: title,
        accessToken: accessToken1,
      );
      const targetCalendar2 = TargetCalendar(
        id: id,
        title: title,
        accessToken: accessToken,
      );
      expect(targetCalendar1, isNot(equals(targetCalendar2)));
    });

    test('should have the same hash code for TargetCalendars with the values',
        () {
      const targetCalendar1 = TargetCalendar(
        id: id,
        title: title,
        accessToken: accessToken,
      );
      const targetCalendar2 = TargetCalendar(
        id: id,
        title: title,
        accessToken: accessToken,
      );
      expect(targetCalendar1.hashCode, equals(targetCalendar2.hashCode));
    });
  });
}
