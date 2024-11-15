import 'package:freezed_annotation/freezed_annotation.dart';

part 'ics_validation_status.freezed.dart';

@freezed
class IcsValidationStatus with _$IcsValidationStatus {
  const IcsValidationStatus._();

  const factory IcsValidationStatus.notValidated() = NotValidated;
  const factory IcsValidationStatus.validationInProgress() =
      ValidationInProgress;

  /// When the URL is valid and the ICS content has been successfully validated
  const factory IcsValidationStatus.validated({int? nbEvents}) = Validated;

  /// When the URL is invalid (e.g. not a URL, content too long or not available...)
  const factory IcsValidationStatus.invalid({required String? errorMessage}) =
      Invalid;

  /// If an error occured during the validation process (e.g. network error, server error...)
  const factory IcsValidationStatus.validationFailed(
      {required String? errorMessage}) = ValidationFailed;

  bool get isValidated => this is Validated;
  bool get isLoading => this is ValidationInProgress;
}
