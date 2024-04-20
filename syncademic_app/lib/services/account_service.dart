import '../models/user.dart';

class AccountService {
  Future<void> createAccount(User user) async {}
}

class MockAccountService extends AccountService {
  @override
  Future<void> createAccount(User user) async {
    // Mock implementation
  }
}
