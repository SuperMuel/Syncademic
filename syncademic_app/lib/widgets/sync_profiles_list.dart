import 'package:flutter/material.dart';
import 'package:get_it/get_it.dart';
import 'package:syncademic_app/repository/sync_profile_repository.dart';

import '../models/sync_profile.dart';

class SyncProfilesList extends StatelessWidget {
  const SyncProfilesList({super.key});

  @override
  Widget build(BuildContext context) {
    final repo = GetIt.instance<SyncProfileRepository>();

    return StreamBuilder(
        stream: repo.getSyncProfiles(),
        builder: (context, snapshot) {
          if (snapshot.hasError) {
            return Text('Error: ${snapshot.error}');
          }

          if (!snapshot.hasData) {
            return const CircularProgressIndicator();
          }
          final profiles = snapshot.data as List<SyncProfile>;
          return _List(profiles: profiles);
        });
  }
}

class _List extends StatelessWidget {
  final List<SyncProfile> profiles;
  const _List({required this.profiles});

  //TODO: Add a message when the list is empty
  @override
  Widget build(BuildContext context) {
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
