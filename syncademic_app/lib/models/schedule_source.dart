import 'package:equatable/equatable.dart';

class ScheduleSource extends Equatable {
  final String id;
  final String url;

  const ScheduleSource({required this.id, required this.url});

  @override
  List<Object?> get props => [id, url];
}
