import 'dart:async';

import 'package:google_sign_in/google_sign_in.dart';

import 'package:quiver/strings.dart';
import '../models/provider_account.dart';

abstract class ProviderAccountService {
  /// Opens a dialog to select a provider account.
  Future<ProviderAccount?> triggerProviderAccountSelection();

  /// Resets the current provider account so that the next call
  /// to [triggerProviderAccountSelection] will open the dialog instead
  /// of returning a cached value.
  Future<void> reset();

  Stream<ProviderAccount?> get onCurrentUserChanged;
}

class MockProviderAccountService implements ProviderAccountService {
  @override
  Future<ProviderAccount> triggerProviderAccountSelection() async {
    await Future.delayed(const Duration(microseconds: 1));
    return const ProviderAccount(
      provider: Provider.google,
      providerAccountId: 'mock-provider-account-id',
      providerAccountEmail: 'info@syncademic.io',
    );
  }

  @override
  Future<void> reset() async {
    await Future.delayed(const Duration(microseconds: 1));
  }

  @override
  Stream<ProviderAccount?> get onCurrentUserChanged =>
      Stream.value(const ProviderAccount(
        provider: Provider.google,
        providerAccountId: 'mock-provider-account-id',
        providerAccountEmail: 'info@syncademic.io',
      ));
}

class GoogleProviderAccountService implements ProviderAccountService {
  final GoogleSignIn googleSignIn;

  GoogleProviderAccountService({required this.googleSignIn});

  @override
  Stream<ProviderAccount?> get onCurrentUserChanged =>
      googleSignIn.onCurrentUserChanged.map((GoogleSignInAccount? account) {
        if (account == null) {
          return null;
        }

        return ProviderAccount(
          provider: Provider.google,
          providerAccountId: account.id,
          providerAccountEmail: account.email,
        );
      });

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
      provider: Provider.google,
      providerAccountId: user.id,
      providerAccountEmail: user.email,
    );
  }

  @override
  Future<void> reset() => googleSignIn.signOut();
}
