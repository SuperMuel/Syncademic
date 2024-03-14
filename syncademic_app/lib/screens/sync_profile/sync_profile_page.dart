import 'package:flutter/material.dart';
import 'package:get_it/get_it.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:syncademic_app/models/id.dart';
import 'package:syncademic_app/models/sync_profile.dart';
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
  const _SyncProfileBody({required this.syncProfile});

  final SyncProfile syncProfile;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Sync Profile ID',
            style: GoogleFonts.montserrat(
              fontWeight: FontWeight.bold,
              fontSize: 18,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            syncProfile.id.value,
            style: GoogleFonts.montserrat(fontSize: 16),
          ),
          const SizedBox(height: 24),
          Text(
            'Schedule Source',
            style: GoogleFonts.montserrat(
              fontWeight: FontWeight.bold,
              fontSize: 18,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            syncProfile.scheduleSource.url,
            style: GoogleFonts.montserrat(fontSize: 16),
          ),
          const SizedBox(height: 24),
          Text(
            'Target Calendar',
            style: GoogleFonts.montserrat(
              fontWeight: FontWeight.bold,
              fontSize: 18,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'ID: ${syncProfile.targetCalendar.id.value}',
            style: GoogleFonts.montserrat(fontSize: 16),
          ),
          const SizedBox(height: 8),
          Text(
            'Title: ${syncProfile.targetCalendar.title}',
            style: GoogleFonts.montserrat(fontSize: 16),
          ),
          const SizedBox(height: 32),
          Row(
            mainAxisAlignment: MainAxisAlignment.end,
            children: [
              ElevatedButton.icon(
                onPressed: null, // TODO implement "Sync Now"
                icon: const Icon(Icons.sync),
                label: const Text('Synchronize Now'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.green,
                  foregroundColor: Colors.white,
                ),
              ),
              const SizedBox(width: 16),
              ElevatedButton.icon(
                onPressed: () {
                  GetIt.I<SyncProfileRepository>()
                      .deleteSyncProfile(syncProfile.id);
                  context.pop();
                },
                icon: const Icon(Icons.delete),
                label: const Text('Delete'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.red,
                  foregroundColor: Colors.white,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _NotFoundBody extends StatelessWidget {
  const _NotFoundBody({super.key});

  @override
  Widget build(BuildContext context) {
    return const Center(
      child: Text(
        'Sync Profile not found',
        style: TextStyle(
          fontSize: 18,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }
}

// class _SyncProfileBody extends StatelessWidget {
//   const _SyncProfileBody({super.key, this.syncProfile});

//   final syncProfile;

//   @override
//   Widget build(BuildContext context) {
//     return Column(
//       children: [
//         Text(syncProfile.id.value),
//         Text(syncProfile.scheduleSource.url),
//         Text(syncProfile.targetCalendar.id.value),
//         Text(syncProfile.targetCalendar.title),
//       ],
//     );
//   }
// }

// class _NotFoundBody extends StatelessWidget {
//   const _NotFoundBody({super.key});

//   @override
//   Widget build(BuildContext context) {
//     return const Center(child: Text('Sync Profile not found'));
//   }
// }
