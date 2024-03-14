import 'package:flutter/material.dart';
import 'package:get_it/get_it.dart';
import 'package:syncademic_app/models/id.dart';
import 'package:syncademic_app/repositories/sync_profile_repository.dart';

class SyncProfilePage extends StatelessWidget {
  const SyncProfilePage({super.key, required this.syncProfileId});
  final String syncProfileId;

  @override
  Widget build(BuildContext context) {
    final syncProfileRepository = GetIt.I<SyncProfileRepository>();

    final syncProfileStream = syncProfileRepository
        .watchSyncProfile(ID.fromTrustedSource(syncProfileId));

    return StreamBuilder(
        stream: syncProfileStream,
        builder: (context, snapshot) {
          final syncProfile = snapshot.data;
          return Scaffold(
            appBar: AppBar(
              title: const Text('Sync Profile'),
            ),
            body: SafeArea(
              child: syncProfile != null
                  ? _SyncProfileBody(syncProfile: syncProfile)
                  : const _NotFoundBody(),
            ),
          );
        });
  }
}

class _SyncProfileBody extends StatelessWidget {
  const _SyncProfileBody({super.key, this.syncProfile});

  final syncProfile;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(syncProfile.id.value),
        Text(syncProfile.scheduleSource.url),
        Text(syncProfile.targetCalendar.id.value),
        Text(syncProfile.targetCalendar.title),
      ],
    );
  }
}

class _NotFoundBody extends StatelessWidget {
  const _NotFoundBody({super.key});

  @override
  Widget build(BuildContext context) {
    return const Center(child: Text('Sync Profile not found'));
  }
}
