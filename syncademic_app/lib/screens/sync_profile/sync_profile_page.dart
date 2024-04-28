import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:get_it/get_it.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:syncademic_app/widgets/schedule_source_card.dart';
import 'package:syncademic_app/widgets/sync_profile_status_card.dart';
import '../../widgets/target_calendar_card.dart';

import '../../models/sync_profile.dart';
import '../../repositories/sync_profile_repository.dart';
import 'cubit/sync_profile_cubit.dart';

class SyncProfilePage extends StatelessWidget {
  const SyncProfilePage({super.key});

  @override
  Widget build(BuildContext context) =>
      BlocConsumer<SyncProfileCubit, SyncProfileState>(
        listener: (context, state) {
          state.maybeMap(
            loaded: (loaded) {
              if (loaded.requestSyncError != null) {
                ScaffoldMessenger.of(context)
                  ..clearSnackBars()
                  ..showSnackBar(
                    SnackBar(
                      content: Text(loaded.requestSyncError!),
                    ),
                  );
              }
            },
            orElse: () {},
          );
        },
        builder: (context, state) {
          return Scaffold(
            appBar: AppBar(
              title: state.appbarTitle,
              actions: state.toAppbarActions(context, state),
            ),
            body: SafeArea(
              child: SingleChildScrollView(
                child: state.map(
                  loading: (_) =>
                      const Center(child: CircularProgressIndicator()),
                  loaded: (loaded) =>
                      _SyncProfileBody(syncProfile: loaded.syncProfile),
                  notFound: (_) => const _NotFoundBody(),
                ),
              ),
            ),
          );
        },
      );
}

extension on SyncProfileState {
  List<Widget> toAppbarActions(BuildContext context, SyncProfileState state) =>
      maybeMap(
        loaded: (loaded) => [
          // Synchronize now button
          IconButton(
            icon: const Icon(Icons.sync),
            tooltip: "Synchronize now",
            onPressed: state.canRequestSync
                ? context.read<SyncProfileCubit>().requestSync
                : null,
          ),
          // Delete button
          IconButton(
            icon: const Icon(Icons.delete),
            tooltip: "Delete this synchronization",
            onPressed: () {
              GetIt.I<SyncProfileRepository>() // TODO : move this call to cubit and show a confirmation dialog
                  .deleteSyncProfile(loaded.syncProfile.id);
              context.pop();
            },
          ),
        ],
        orElse: () => [],
      );
  Text get appbarTitle => maybeMap(
        loaded: (loaded) => Text(loaded.syncProfile.title),
        notFound: (_) => const Text('Sync Profile not found'),
        orElse: () => const Text('Sync Profile Details'),
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
            'Schedule Source',
            style: GoogleFonts.montserrat(
              fontWeight: FontWeight.bold,
              fontSize: 18,
            ),
          ),
          const SizedBox(height: 8),
          ScheduleSourceCard(scheduleSource: syncProfile.scheduleSource),
          const SizedBox(height: 24),
          Text(
            'Target Calendar',
            style: GoogleFonts.montserrat(
              fontWeight: FontWeight.bold,
              fontSize: 18,
            ),
          ),
          TargetCalendarCard(targetCalendar: syncProfile.targetCalendar),
          const SizedBox(height: 32),

          // Status
          Text(
            'Status',
            style: GoogleFonts.montserrat(
              fontWeight: FontWeight.bold,
              fontSize: 18,
            ),
          ),

          SyncProfileStatusCard(status: syncProfile.status)
        ],
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
