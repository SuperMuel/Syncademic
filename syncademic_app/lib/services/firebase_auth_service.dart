import 'dart:async';

import 'package:firebase_auth/firebase_auth.dart';
import 'auth_service.dart';

import '../models/user.dart' as syncademic;

class FirebaseAuthService extends AuthService {
  final FirebaseAuth _firebaseAuth;

  FirebaseAuthService({FirebaseAuth? firebaseAuth})
      : _firebaseAuth = firebaseAuth ?? FirebaseAuth.instance;

  @override
  Future<syncademic.User?> signInWithGoogle() async {
    try {
      GoogleAuthProvider googleProvider = GoogleAuthProvider();

      // Once signed in, return the UserCredential
      final userCredential =
          await _firebaseAuth.signInWithPopup(googleProvider);

      final syncademicUser = userCredential.toSyncademicUser;

      return syncademicUser;
    } on FirebaseAuthException catch (_) {
      // TODO handle error
      rethrow;
    }
  }

  @override
  Future<void> signOut() async {
    await _firebaseAuth.signOut();
  }

  @override
  Stream<syncademic.User?> get authStateChanges =>
      _firebaseAuth.authStateChanges().map((user) => user?.toSyncademicUser);

  @override
  Future<syncademic.User?> get currentUser async =>
      _firebaseAuth.currentUser?.toSyncademicUser;
}

extension on User {
  syncademic.User get toSyncademicUser => syncademic.User(
        id: uid,
      );
}

extension on UserCredential {
  syncademic.User get toSyncademicUser => syncademic.User(
        id: user!.uid,
      );
}
