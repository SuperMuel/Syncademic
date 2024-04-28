import 'package:flutter/material.dart';
import '../models/sync_profile_status.dart';
import 'last_synchronized.dart';

class SyncProfileStatusCard extends StatelessWidget {
  final SyncProfileStatus? status;

  const SyncProfileStatusCard({super.key, required this.status});

  @override
  Widget build(BuildContext context) {
    if (status == null) {
      return const Card(
          child: ListTile(
        title: Text('No status'),
        leading: Icon(Icons.sync_problem),
      ));
    }

    return Card(
      child: ListTile(
        title: Text(status!.title),
        leading: status!.leadingIcon,
        onTap: status!.onTap != null ? () => status!.onTap!(context) : null,
        subtitle: LastSynchronized(
          lastSync: status!.lastSuccessfulSync,
          builder: (context, lastSync) => Text("Last sync: $lastSync"),
        ),
      ),
    );
  }
}

extension on SyncProfileStatus {
  String get title => map(
        success: (_) => 'Synced successfully',
        inProgress: (_) => 'Synchronizing',
        failed: (_) => 'Synchronization failed',
        notStarted: (_) => 'Synchronization will start soon',
      )!;

  Widget get leadingIcon => map(
        success: (_) => const Icon(Icons.check, color: Colors.green),
        inProgress: (_) => const CircularProgressIndicator(),
        failed: (_) => const Icon(Icons.error, color: Colors.red),
        notStarted: (_) => const Icon(Icons.sync_problem),
      )!;

  Function(BuildContext)? get onTap => maybeMap(
        orElse: () => null,
        failed: (failed) => (context) {
          ScaffoldMessenger.of(context)
            ..clearSnackBars()
            ..showSnackBar(
              SnackBar(
                content: Text('Error: ${failed.message}'),
              ),
            );
        },
      );
}
