import 'dart:async';

import 'package:google_sign_in/google_sign_in.dart';

import 'package:quiver/strings.dart';
import 'package:syncademic_app/models/id.dart';
import 'package:syncademic_app/models/provider_account.dart';

abstract class ProviderAccountService {
  /// Opens a dialog to select a provider account.
  Future<ProviderAccount?> triggerProviderAccountSelection();

  /// Resets the current provider account so that the next call
  /// to [triggerProviderAccountSelection] will open the dialog instead
  /// of returning a cached value.
  Future<void> reset();
}

class MockProviderAccountService implements ProviderAccountService {
  @override
  Future<ProviderAccount> triggerProviderAccountSelection() async {
    await Future.delayed(const Duration(microseconds: 1));
    return const ProviderAccount(
      id: ID.fromString('mock-provider-account-id'),
      provider: Provider.google,
      providerAccountId: 'mock-provider-account-id',
      providerAccountEmail: 'info@syncademic.io',
    );
  }

  @override
  Future<void> reset() async {
    await Future.delayed(const Duration(microseconds: 1));
  }
}

class GoogleProviderAccountService implements ProviderAccountService {
  final GoogleSignIn googleSignIn;

  GoogleProviderAccountService({required this.googleSignIn})

  @override
  Future<ProviderAccount?> triggerProviderAccountSelection() async {
    GoogleSignInAccount? user = await googleSignIn.signIn();

    if (user == null) {
      return null;
    }

    if (isEmpty(user.id)) {
      throw Exception("User ID should not be empty.");
    }

    if (isEmpty(user.email)) {
      throw Exception("User email should not be empty.");
    }

    return ProviderAccount(
      id: null,
      provider: Provider.google,
      providerAccountId: user.id,
      providerAccountEmail: user.email,
    );
  }

  @override
  Future<void> reset() => googleSignIn.signOut();
}
