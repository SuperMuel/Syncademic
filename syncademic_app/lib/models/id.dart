import 'package:equatable/equatable.dart';
import 'package:uuid/uuid.dart';

class ID extends Equatable {
  /// The value of the ID
  final String value;

  /// Generates a new v4 UUID
  ID() : value = const Uuid().v4();

  /// Creates a new ID from a trusted source
  const ID.fromTrustedSource(this.value);

  @override
  List<Object> get props => [value];
}
