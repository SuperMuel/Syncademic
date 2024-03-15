import 'package:flutter_test/flutter_test.dart';
import 'package:syncademic_app/models/user.dart';

void main() {
  const id = '1';
  const email = 'test1@example.com';

  test('should create a User instance', () {
    const user = User(id: id, email: email);

    expect(user.id, id);
    expect(user.email, email);
  });

  group('equals', () {
    test('should be equal to another User with the same id and email', () {
      const user1 = User(id: id, email: email);
      const user2 = User(id: id, email: email);
      expect(user1, equals(user2));
    });

    test('should not be equal to another User with a different id', () {
      const id1 = '2';
      const user1 = User(id: id1, email: email);
      const user2 = User(id: id, email: email);
      expect(user1, isNot(equals(user2)));
    });

    test('should not be equal to another User with a different email', () {
      const email1 = 'example@exaplejefeij.com';
      const user1 = User(id: id, email: email1);
      const user2 = User(id: id, email: email);
      expect(user1, isNot(equals(user2)));
    });

    test('should have the same hash code for Users with the same id and email',
        () {
      const user1 = User(id: id, email: email);
      const user2 = User(id: id, email: email);
      expect(user1.hashCode, equals(user2.hashCode));
    });
  });
}
