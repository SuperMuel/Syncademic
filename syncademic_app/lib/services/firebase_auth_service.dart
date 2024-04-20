import 'dart:async';
import 'dart:developer';

import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/foundation.dart';
import 'package:get_it/get_it.dart';
import 'package:google_sign_in/google_sign_in.dart';

import '../models/user.dart' as syncademic;
import 'account_service.dart';
import 'auth_service.dart';

class FirebaseAuthService extends AuthService {
  final FirebaseAuth _firebaseAuth;

  FirebaseAuthService({FirebaseAuth? firebaseAuth})
      : _firebaseAuth = firebaseAuth ?? FirebaseAuth.instance;

  Future<UserCredential> _signInWithGoogleMobile() async {
    log("Signing in with Google (Mobile)");
    // Trigger the authentication flow
    final GoogleSignInAccount? googleUser = await GoogleSignIn().signIn();

    if (googleUser == null) {
      log("Google user is null");
      //TODO : Check if this is the correct way to handle this
      throw Exception('Google sign in aborted');
    }

    log("Google user signed in");

    // Obtain the auth details from the request
    final GoogleSignInAuthentication googleAuth =
        await googleUser.authentication;

    // Create a new credential
    final credential = GoogleAuthProvider.credential(
      accessToken: googleAuth.accessToken,
      idToken: googleAuth.idToken,
    );

    // Once signed in, return the UserCredential
    return await FirebaseAuth.instance.signInWithCredential(credential);
  }

  Future<UserCredential> _signInWithGoogleWeb() async {
    GoogleAuthProvider googleProvider = GoogleAuthProvider();

    return await _firebaseAuth.signInWithPopup(googleProvider);
  }

  @override
  Future<syncademic.User?> signInWithGoogle() async {
    try {
      UserCredential userCredential;

      if (kIsWeb) {
        userCredential = await _signInWithGoogleWeb();
      } else {
        userCredential = await _signInWithGoogleMobile();
      }

      final syncademicUser = userCredential.toSyncademicUser;

      // Create the user in the database if it doesn't exist
      GetIt.I<AccountService>().createAccount(syncademicUser);

      return syncademicUser;
    } on FirebaseAuthException catch (e) {
      log('Error signing in with Google', error: e);
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
  syncademic.User? get currentUser =>
      _firebaseAuth.currentUser?.toSyncademicUser;
}

extension on User {
  syncademic.User get toSyncademicUser => syncademic.User(
        id: uid,
        email: email,
      );
}

extension on UserCredential {
  syncademic.User get toSyncademicUser => syncademic.User(
        id: user!.uid,
        email: user!.email,
      );
}
