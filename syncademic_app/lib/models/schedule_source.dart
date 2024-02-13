import 'package:equatable/equatable.dart';
import 'id.dart';

class ScheduleSource extends Equatable {
  final ID id;
  final String url;

  const ScheduleSource({required this.id, required this.url});

  @override
  List<Object?> get props => [id, url];
}
