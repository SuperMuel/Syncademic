import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:syncademic_app/models/target_calendar.dart';

import 'target_calendar_selector_cubit.dart';

class TargetCalendarSelector extends StatelessWidget {
  const TargetCalendarSelector({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<TargetCalendarSelectorCubit,
        TargetCalendarSelectorState>(
      builder: (context, state) {
        switch (state.authorizationStatus) {
          case AuthorizationStatus.unauthorized:
            return const _UnauthorizedBody();
          case AuthorizationStatus.authorizing:
            return const Center(
              child: CircularProgressIndicator(),
            );
          case AuthorizationStatus.authorized:
            return TargetCalendarList(calendars: state.calendars);
        }
      },
    );
  }
}

class _UnauthorizedBody extends StatelessWidget {
  const _UnauthorizedBody();

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: <Widget>[
        const Text(
          'You need to authorize Syncademia to access your calendars',
          textAlign: TextAlign.center,
          style: TextStyle(fontSize: 16),
        ),
        const SizedBox(height: 20),
        ElevatedButton(
          onPressed: () =>
              context.read<TargetCalendarSelectorCubit>().authorize(),
          child: const Text('Authorize'),
        ),
      ],
    );
  }
}

class TargetCalendarList extends StatelessWidget {
  const TargetCalendarList({super.key, required this.calendars});

  final List<TargetCalendar> calendars;

  @override
  Widget build(BuildContext context) {
    return DropdownButton(
      hint: const Text('Select a calendar'),
      items: calendars
          .map((calendar) => DropdownMenuItem(
                value: calendar,
                child: Text(calendar.title),
              ))
          .toList(),
      onChanged: context.read<TargetCalendarSelectorCubit>().selectCalendar,
    );
  }
}
