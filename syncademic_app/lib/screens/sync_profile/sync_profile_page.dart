import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:get_it/get_it.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';

import '../../models/sync_profile.dart';
import '../../models/sync_profile_status.dart';
import '../../repositories/sync_profile_repository.dart';
import 'cubit/sync_profile_cubit.dart';

class SyncProfilePage extends StatelessWidget {
  const SyncProfilePage({super.key});

  @override
  Widget build(BuildContext context) =>
      BlocBuilder<SyncProfileCubit, SyncProfileState>(
        builder: (context, state) {
          return Scaffold(
            appBar: AppBar(
              title: const Text('Sync Profile Details'),
            ),
            body: SafeArea(
              child: SingleChildScrollView(
                child: state.when(
                  loading: () =>
                      const Center(child: CircularProgressIndicator()),
                  loaded: (syncProfile) =>
                      _SyncProfileBody(syncProfile: syncProfile),
                  notFound: () => const _NotFoundBody(),
                ),
              ),
            ),
          );
        },
      );
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
          SelectableText(
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
          SelectableText(
            'ID: ${syncProfile.targetCalendar.id.value}',
            style: GoogleFonts.montserrat(fontSize: 16),
          ),
          const SizedBox(height: 8),
          SelectableText(
            'Title: ${syncProfile.targetCalendar.title}',
            style: GoogleFonts.montserrat(fontSize: 16),
          ),
          const SizedBox(height: 32),

          // Last synchronized
          Text(
            'Last Synchronized',
            style: GoogleFonts.montserrat(
              fontWeight: FontWeight.bold,
              fontSize: 18,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            syncProfile.lastSuccessfulSync != null
                ? syncProfile.lastSuccessfulSync.toString()
                : 'Never',
            style: GoogleFonts.montserrat(fontSize: 16),
          ),
          const SizedBox(height: 32),

          // Status
          Text(
            'Status',
            style: GoogleFonts.montserrat(
              fontWeight: FontWeight.bold,
              fontSize: 18,
            ),
          ),

          SelectableText(
            '${syncProfile.status}',
            style: GoogleFonts.montserrat(fontSize: 16),
          ),

          const SizedBox(height: 32),

          Row(
            mainAxisAlignment: MainAxisAlignment.end,
            children: [
              const _AuthorizeButton(),
              const SizedBox(width: 16),
              _RequestSyncButton(syncProfile: syncProfile),
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

class _AuthorizeButton extends StatelessWidget {
  const _AuthorizeButton();

  @override
  Widget build(BuildContext context) {
    return ElevatedButton.icon(
      onPressed: context.read<SyncProfileCubit>().authorizeBackend,
      icon: const Icon(Icons.lock),
      label: const Text('Authorize Backend'),
      style: ElevatedButton.styleFrom(
        backgroundColor: Colors.blue,
        foregroundColor: Colors.white,
      ),
    );
  }
}

class _RequestSyncButton extends StatelessWidget {
  final SyncProfile syncProfile;

  const _RequestSyncButton({
    required this.syncProfile,
  });

  @override
  Widget build(BuildContext context) {
    final canRequestSync =
        syncProfile.status != const SyncProfileStatus.inProgress();

    return ElevatedButton.icon(
      onPressed:
          canRequestSync ? context.read<SyncProfileCubit>().requestSync : null,
      icon: const Icon(Icons.sync),
      label: const Text('Synchronize Now'),
      style: ElevatedButton.styleFrom(
        backgroundColor: Colors.green,
        foregroundColor: Colors.white,
      ),
    );
  }
}

class _NotFoundBody extends StatelessWidget {
  const _NotFoundBody();

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
