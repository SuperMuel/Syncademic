import 'package:equatable/equatable.dart';
import 'package:syncademic_app/models/schedule_source.dart';

/// A synchronization profile.
///
/// A synchronization profile is a configuration that
/// tells what, when and how to synchronize a university schedule
/// with the user's calendar.
class SyncProfile extends Equatable {
  final String id;
  final bool enabled;
  final ScheduleSource scheduleSource;

  const SyncProfile({
    required this.id,
    required this.scheduleSource,
    this.enabled = false,
  });

  @override
  List<Object?> get props => [id, enabled, scheduleSource];
}
