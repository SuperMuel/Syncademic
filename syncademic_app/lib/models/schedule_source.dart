import 'package:equatable/equatable.dart';

class ScheduleSource extends Equatable {
  final String url;

  const ScheduleSource({required this.url});

  @override
  List<Object?> get props => [url];
}
