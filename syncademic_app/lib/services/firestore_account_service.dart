import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:syncademic_app/models/user.dart';
import 'account_service.dart';

class FirebaseAccountService extends AccountService {
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;

  Future<bool> accountExists(String uid) async {
    try {
      final doc = await _firestore.collection('users').doc(uid).get();
      return doc.exists;
    } catch (e) {
      print(e);
      // TODO handle error
      rethrow;
    }
  }

  @override
  Future<void> createAccount(User user) async {
    if (await accountExists(user.id)) {
      return;
    }
    try {
      await _firestore.collection('users').doc(user.id).set({
        'email': user.email,
      });
    } catch (e) {
      // TODO handle error
      print(e);
      rethrow;
    }
  }
}
