import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:syncademic_app/models/sync_profile.dart';
import 'package:syncademic_app/screens/sync_profile/cubit/sync_profile_cubit.dart';
import 'package:syncademic_app/screens/sync_profile_2/cubit/sync_profile_2_cubit.dart';

class SyncProfilePage extends StatelessWidget {
  const SyncProfilePage({super.key});

  @override
  Widget build(BuildContext context) {
    final bloc = context.read<SyncProfile_2Cubit>();

    return BlocBuilder<SyncProfile_2Cubit, SyncProfile_2State>(
      builder: (context, state) {
        final syncProfile = state.syncProfile;
        return Scaffold(
          appBar: AppBar(
            title: Text(syncProfile.title),
            actions: [
              IconButton(
                icon: const Icon(Icons.sync),
                tooltip: "Synchronize now",
                onPressed: state.canRequestSync ? bloc.requestSync : null,
              ),
              // Delete button
              IconButton(
                icon: const Icon(Icons.delete),
                tooltip: "Delete this synchronization",
                onPressed: context.read<SyncProfileCubit>().requestDeletion,
              ),
            ],
          ),
        );
      },
    );
  }
}
