import 'package:flutter/material.dart';

import '../models/sync_profile.dart';

class SyncProfilesList extends StatelessWidget {
  final List<SyncProfile> profiles;

  const SyncProfilesList({super.key, required this.profiles});

  @override
  Widget build(BuildContext context) {
    //TODO: Add a message when the list is empty
    return ListView.builder(
      itemCount: profiles.length,
      itemBuilder: (context, index) {
        final profile = profiles[index];
        return ListTile(
          title: Text(profile.scheduleSource.url),
          subtitle: Text(profile.enabled ? 'Enabled' : 'Disabled'),
        );
      },
    );
  }
}
