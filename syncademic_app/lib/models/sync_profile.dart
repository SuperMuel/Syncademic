import 'package:equatable/equatable.dart';

import 'id.dart';
import 'schedule_source.dart';
import 'target_calendar.dart';

/// A synchronization profile.
///
/// A synchronization profile is a configuration that
/// tells what, when and how to synchronize a university schedule
/// with the user's calendar.
class SyncProfile extends Equatable {
  final ID id;
  final bool enabled;
  //final String title;
  final ScheduleSource scheduleSource;
  final TargetCalendar targetCalendar;

  const SyncProfile({
    required this.id,
    required this.scheduleSource,
    required this.targetCalendar,
    //required this.title,
    this.enabled = false,
  });

  @override
  List<Object?> get props => [
        id,
        enabled,
        //title,

        scheduleSource,
        targetCalendar,
      ];
}
