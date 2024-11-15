import 'package:freezed_annotation/freezed_annotation.dart';

part 'ics_validation_status.freezed.dart';

@freezed
class IcsValidationStatus with _$IcsValidationStatus {
  const IcsValidationStatus._();

  const factory IcsValidationStatus.notValidated() = NotValidated;
  const factory IcsValidationStatus.validationInProgress() =
      ValidationInProgress;
  const factory IcsValidationStatus.validated({int? nbEvents}) = Validated;
  const factory IcsValidationStatus.validationFailed(
      {required String? errorMessage}) = ValidationFailed;

  bool get isValidated => this is Validated;
}
