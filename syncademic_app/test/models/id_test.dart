import 'package:syncademic_app/models/id.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('id should have correct value when created using default constructor',
      () {
    final id = ID();
    expect(id.value, isNotNull);
    expect(id.value, isNotEmpty);
  });

  test(
      'id should have unique values when created using default constructor multiple times',
      () {
    final id1 = ID();
    final id2 = ID();
    expect(id1.value, isNot(equals(id2.value)));
  });

  test(
      'id should have correct value when created using trusted source constructor',
      () {
    const value = 'example_id';
    const id = ID.fromString(value);
    expect(id.value, equals(value));
  });

  test('id should be equal to another id with the same value', () {
    const value = 'example_id';
    const id1 = ID.fromString(value);
    const id2 = ID.fromString(value);
    expect(id1, equals(id2));
  });
}
