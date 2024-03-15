import 'package:equatable/equatable.dart';

class User extends Equatable {
  const User({required this.id, this.email});

  final String id;
  final String? email;

  @override
  List<Object?> get props => [id, email];
}
