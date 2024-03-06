import 'package:equatable/equatable.dart';
import 'id.dart';

class TargetCalendar extends Equatable {
  final ID id;
  final String title;
  final String? accessToken;
  //TODO(SuperMuel) also get refresh token

  final bool? backendHasAccess;

  const TargetCalendar({
    required this.id,
    required this.title,
    this.accessToken,
    this.backendHasAccess,
  });

  @override
  List<Object?> get props => [id, title, accessToken];
}
