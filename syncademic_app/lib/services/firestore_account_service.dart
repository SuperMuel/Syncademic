import 'dart:developer';

import 'package:cloud_firestore/cloud_firestore.dart';

import '../models/user.dart';
import 'account_service.dart';

class FirebaseAccountService extends AccountService {
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;

  Future<bool> accountExists(String uid) async {
    try {
      final doc = await _firestore.collection('users').doc(uid).get();
      return doc.exists;
    } catch (e) {
      log('Error checking if account exists', error: e);
      rethrow;
    }
  }

  @override
  Future<void> createAccount(User user) async {
    // TODO: Move this behavior to a cloud function for safety.

    if (await accountExists(user.id)) {
      return;
    }
    try {
      await _firestore.collection('users').doc(user.id).set({
        'email': user.email,
      });
    } catch (e) {
      log('Error creating account', error: e);
      rethrow;
    }
  }
}
