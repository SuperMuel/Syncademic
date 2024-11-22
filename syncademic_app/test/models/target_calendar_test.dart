import 'package:flutter_test/flutter_test.dart';
import 'package:syncademic_app/models/id.dart';
import 'package:syncademic_app/models/target_calendar.dart';

void main() {
  const id = ID.fromString('test_id');
  const title = 'Test Title';
  const providerAccountId = 'providerAccountId';
  const email = 'test@syncademic.io';

  TargetCalendar createTargetCalendar({
    ID id = id,
    String title = title,
    String providerAccountId = providerAccountId,
    String providerAccountEmail = email,
  }) =>
      TargetCalendar(
        id: id,
        title: title,
        providerAccountId: providerAccountId,
        providerAccountEmail: providerAccountEmail,
      );

  test('should create a TargetCalendar instance', () {
    const targetCalendar = TargetCalendar(
      id: id,
      title: title,
      providerAccountId: providerAccountId,
      providerAccountEmail: email,
    );

    expect(targetCalendar.id, id);
    expect(targetCalendar.title, title);
    expect(targetCalendar.providerAccountId, providerAccountId);
    expect(targetCalendar.providerAccountEmail, email);
  });

  group('equals', () {
    test('should be equal to another TargetCalendar with the values', () {
      final targetCalendar1 = createTargetCalendar();
      final targetCalendar2 = createTargetCalendar();
      expect(targetCalendar1, equals(targetCalendar2));
    });

    test('should not be equal to another TargetCalendar with a different id',
        () {
      final targetCalendar1 =
          createTargetCalendar(id: const ID.fromString("A"));
      final targetCalendar2 =
          createTargetCalendar(id: const ID.fromString("B"));

      expect(targetCalendar1, isNot(equals(targetCalendar2)));
    });

    test('should not be equal to another TargetCalendar with a different title',
        () {
      final targetCalendar1 = createTargetCalendar(title: 'A');
      final targetCalendar2 = createTargetCalendar(title: 'B');

      expect(targetCalendar1, isNot(equals(targetCalendar2)));
    });

    test(
        'should not be equal to another TargetCalendar with a different providerAccountId',
        () {
      final targetCalendar1 = createTargetCalendar(providerAccountId: 'A');
      final targetCalendar2 = createTargetCalendar(providerAccountId: 'B');

      expect(targetCalendar1, isNot(equals(targetCalendar2)));
    });

    test(
        'should not be equal to another TargetCalendar with a different providerAccountEmail',
        () {
      final targetCalendar1 = createTargetCalendar(providerAccountEmail: 'testA@syncademic.io');
      final targetCalendar2 = createTargetCalendar(providerAccountEmail: 'testB@syncademic.io'); 

      expect(targetCalendar1, isNot(equals(targetCalendar2)));
    });


    test(
        'should have the same hash code for TargetCalendars with the same values',
        () {
      final targetCalendar1 = createTargetCalendar();
      final targetCalendar2 = createTargetCalendar();

      expect(targetCalendar1.hashCode, equals(targetCalendar2.hashCode));
    });
  });
}
