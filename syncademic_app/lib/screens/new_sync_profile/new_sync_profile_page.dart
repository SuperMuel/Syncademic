import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:gap/gap.dart';
import '../../models/target_calendar.dart';
import 'target_calendar_selector/target_calendar_selector_cubit.dart';
import '../../widgets/target_calendar_card.dart';
import 'target_calendar_selector/target_calendar_selector.dart';

import 'new_sync_profile_cubit.dart';

class NewSyncConfigPage extends StatelessWidget {
  const NewSyncConfigPage({super.key});

  @override
  Widget build(BuildContext context) {
    final cubit = context.read<NewSyncProfileCubit>();

    return BlocConsumer<NewSyncProfileCubit, NewSyncProfileState>(
      listener: (context, state) {
        if (state.isSuccess) {
          Navigator.of(context).pop();

          ScaffoldMessenger.of(context)
            ..removeCurrentSnackBar()
            ..showSnackBar(const SnackBar(
              content: Text('Synchronization configuration created'),
            ));
        }
        if (state.errorMessage != null) {
          ScaffoldMessenger.of(context)
            ..removeCurrentSnackBar()
            ..showSnackBar(SnackBar(
              content: Text('Error: ${state.errorMessage}'),
              backgroundColor: Colors.red,
            ));
        }
      },
      builder: (context, state) {
        return Scaffold(
          appBar: AppBar(
            title: const Text('New synchronization configuration'),
          ),
          body: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              children: <Widget>[
                TextFormField(
                  decoration: InputDecoration(
                    labelText: 'Title',
                    border: const OutlineInputBorder(),
                    errorText: state.titleError,
                    hintText: 'L3 - Biologie - 2023-2024',
                  ),
                  enabled: state.canEditTitle,
                  maxLength: 50,
                  onChanged: cubit.titleChanged,
                ),
                const Gap(16),

                //TODO : Show a link or help text to explain how to get the calendar url
                TextFormField(
                  decoration: InputDecoration(
                    labelText: 'Calendar url',
                    border: const OutlineInputBorder(),
                    errorText: state.urlError,
                    counterText: '',
                  ),
                  enabled: state.canEditUrl,
                  maxLength: null,
                  onChanged: cubit.urlChanged,
                ),
                const Gap(16),
                _SelectedTargetCalendar(state),
                const Spacer(),
                ElevatedButton.icon(
                  onPressed: state.canSubmit ? cubit.submit : null,
                  icon: const Icon(Icons.save),
                  label: const Text('Synchonize now'),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}

class _SelectedTargetCalendar extends StatelessWidget {
  const _SelectedTargetCalendar(this.state);

  final NewSyncProfileState state;

  @override
  Widget build(BuildContext context) => state.selectedCalendar == null
      ? const _SelectTargetCalendar()
      : TargetCalendarCard(targetCalendar: state.selectedCalendar!);
}

class _SelectTargetCalendar extends StatelessWidget {
  const _SelectTargetCalendar();

  @override
  Widget build(BuildContext context) {
    return ElevatedButton.icon(
      icon: const Icon(Icons.calendar_month),
      onPressed: () {
        // Show dialog
        showDialog<TargetCalendar?>(
          context: context,
          builder: (_) => Dialog(
            child: BlocProvider(
              create: (_) => TargetCalendarSelectorCubit(),
              child: const Padding(
                padding: EdgeInsets.all(8.0),
                child: TargetCalendarSelector(),
              ),
            ),
          ),
        ).then(context.read<NewSyncProfileCubit>().calendarSelected);
      },
      label: const Text('Select target calendar'),
    );
  }
}
