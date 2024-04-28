import 'package:flutter/material.dart';
import 'package:get_it/get_it.dart';

import '../models/sync_profile.dart';
import '../repositories/sync_profile_repository.dart';
import 'last_synchronized.dart';

class SyncProfilesList extends StatelessWidget {
  /// A callback that is called when a profile is tapped.
  final Function(SyncProfile)? onTap;
  const SyncProfilesList({super.key, this.onTap});

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
          return _List(profiles: profiles, onTap: onTap);
        });
  }
}

class _List extends StatelessWidget {
  final List<SyncProfile> profiles;
  final void Function(SyncProfile)? onTap;
  const _List({required this.profiles, this.onTap});

  Widget _emptyList() {
    return const Center(
      child: Text('No sync profiles found.'),
    );
  }

  @override
  Widget build(BuildContext context) {
    return profiles.isEmpty
        ? _emptyList()
        : ListView.builder(
            itemCount: profiles.length,
            itemBuilder: (context, index) {
              final profile = profiles[index];
              return ListTile(
                  title: Text(profile.title,
                      style: Theme.of(context).textTheme.titleLarge),
                  leading: Icon(
                    Icons.sync,
                    color: profile.enabled ? Colors.green : Colors.grey,
                  ),
                  trailing: const Icon(Icons.chevron_right),
                  subtitle: profile.lastSuccessfulSync == null
                      ? const Text('Never synced')
                      : LastSynchronized(
                          lastSync: profile.lastSuccessfulSync,
                          builder: (_, lastSync) =>
                              Text('Last synced: $lastSync')),
                  onTap: onTap == null ? null : () => onTap!(profile));
            },
          );
  }
}
