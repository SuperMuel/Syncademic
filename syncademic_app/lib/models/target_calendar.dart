import 'package:equatable/equatable.dart';
import 'id.dart';

class TargetCalendar extends Equatable {
  final ID id;
  final String title;

  const TargetCalendar({
    required this.id,
    required this.title,
  });

  @override
  List<Object?> get props => [id, title];
}
