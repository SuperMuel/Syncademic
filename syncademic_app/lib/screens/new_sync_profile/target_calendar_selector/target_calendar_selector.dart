import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../../models/target_calendar.dart';
import 'target_calendar_selector_cubit.dart';

class TargetCalendarSelector extends StatelessWidget {
  const TargetCalendarSelector({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Select a target calendar'),
      ),
      body: Center(
        child: BlocBuilder<TargetCalendarSelectorCubit,
            TargetCalendarSelectorState>(builder: (context, state) {
          if (state.loading) {
            return const Center(child: CircularProgressIndicator());
          }

          if (state.error != null) {
            return Center(
              child: Text(state.error!),
            );
          }

          return TargetCalendarList(calendars: state.calendars);
        }),
      ),
    );
  }
}

class TargetCalendarList extends StatelessWidget {
  const TargetCalendarList({super.key, required this.calendars});

  final List<TargetCalendar> calendars;

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      itemCount: calendars.length,
      itemBuilder: (context, index) {
        final calendar = calendars[index];
        return ListTile(
          title: Text(calendar.title),
          subtitle: calendar.description != null
              ? Text(calendar.description!,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: Theme.of(context).textTheme.bodySmall)
              : null,
          onTap: () => Navigator.of(context).pop(calendar),
        );
      },
    );
  }
}
