import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:gap/gap.dart';

import 'new_sync_profile_cubit.dart';

class NewSyncConfigPage extends StatelessWidget {
  const NewSyncConfigPage({super.key});

  @override
  Widget build(BuildContext context) {
    final cubit = context.read<NewSyncProfileCubit>();

    return BlocBuilder<NewSyncProfileCubit, NewSyncProfileState>(
      builder: (context, state) {
        return Scaffold(
          appBar: AppBar(
            title: const Text('New synchronization configuration'),
          ),
          body: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              children: <Widget>[
                //TODO : Show a link or help text to explain how to get the calendar url
                TextFormField(
                  decoration: InputDecoration(
                    labelText: 'Calendar url',
                    border: const OutlineInputBorder(),
                    errorText: state.urlError,
                    counterText: '',
                  ),
                  maxLength: 5000,
                  onChanged: cubit.urlChanged,
                ),
                const Gap(16),
                const Text("This will create a new calendar in your account"),
                const Gap(16),
                ElevatedButton(
                  onPressed: state.canSubmit ? cubit.submit : null,
                  child: const Text('Synchronize'),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}
