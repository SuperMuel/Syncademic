// a providerAccount refers to an account owned by a user on a third-party service, such as Google or Microsoft.
// The user has an account on Syncademic, but also on the third-party service.
//
// For instance, a syncademic user wants to sync their Google Calendar with Syncademic. Their Google account is the providerAccount.

import 'package:freezed_annotation/freezed_annotation.dart';

import 'id.dart';

part 'provider_account.freezed.dart';

enum Provider {
  google;

  String get name {
    switch (this) {
      case Provider.google:
        return 'Google';
    }
  }
}

@freezed

/// Represents a user's account on a third-party service like Google.
///
/// - **Syncademic Account**: The user's account within Syncademic.
/// - **Provider Account**: The user's account on a third-party service (e.g., Google or Microsoft).
class ProviderAccount with _$ProviderAccount {
  const ProviderAccount._();

  const factory ProviderAccount({
    /// The provider of the account (e.g., Google).
    required Provider provider,

    /// The unique ID of the account on the provider's service.
    required String providerAccountId,

    /// The email address associated with the account on the provider's service.
    required String providerAccountEmail,
  }) = _ProviderAccount;
}
