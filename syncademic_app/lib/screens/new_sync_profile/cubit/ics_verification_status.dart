import 'package:freezed_annotation/freezed_annotation.dart';

part 'ics_verification_status.freezed.dart';

@freezed
class IcsVerificationStatus with _$IcsVerificationStatus {
  const IcsVerificationStatus._();

  const factory IcsVerificationStatus.notVerified() = NotVerified;
  const factory IcsVerificationStatus.verificationInProgress() =
      VerificationInProgress;
  const factory IcsVerificationStatus.verified() = Verified;
  const factory IcsVerificationStatus.verificationFailed(
      {required String errorMessage}) = VerificationFailed;

  bool get isVerified => this is Verified;
}
