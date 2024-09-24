import 'dart:math';

import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
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
            return const Center(child: CircularProgressIndicator());
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
  Widget _emptyList(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Image.asset(
              'assets/illustrations/apple_devices_mockup_transparent_1600.png',
              fit: BoxFit.cover,
              width: MediaQuery.of(context).size.width > 600
                  ? 400
                  : MediaQuery.of(context).size.width,
            ),
            const SizedBox(height: 16),
            Text(
              'Create a new Synchronization',
              style: Theme.of(context).textTheme.headlineSmall,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            ConstrainedBox(
              constraints: BoxConstraints(
                  maxWidth: MediaQuery.of(context).size.width > 600
                      ? 400
                      : MediaQuery.of(context).size.width),
              child: Text(
                'A Synchronization allows you to synchronize your university schedule with your Google Calendar. '
                'Tap the button below to create one.',
                style: Theme.of(context).textTheme.bodyMedium,
                textAlign: TextAlign.center,
              ),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return profiles.isEmpty
        ? _emptyList(context)
        : ListView.builder(
            itemCount: profiles.length,
            itemBuilder: (context, index) {
              final profile = profiles[index];
              final lastSuccessfulSync = profile.status?.lastSuccessfulSync;
              return ListTile(
                  title: Text(profile.title,
                      style: Theme.of(context).textTheme.titleLarge),
                  leading: Icon(
                    Icons.sync,
                    color: profile.enabled ? Colors.green : Colors.grey,
                  ),
                  trailing: const Icon(Icons.chevron_right),
                  subtitle: lastSuccessfulSync == null
                      ? const Text('Never synced')
                      : LastSynchronized(
                          lastSync: lastSuccessfulSync,
                          builder: (_, lastSync) =>
                              Text('Last synced: $lastSync')),
                  onTap: onTap == null ? null : () => onTap!(profile));
            },
          );
  }
}
