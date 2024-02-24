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
        ),
      ),
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
        ElevatedButton.icon(
          icon: const Icon(Icons.lock_open),
          onPressed: context.read<TargetCalendarSelectorCubit>().authorize,
          label: const Text('Authorize'),
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
    return ListView.builder(
      itemCount: calendars.length,
      itemBuilder: (context, index) {
        final calendar = calendars[index];
        return ListTile(
          title: Text(calendar.title),
          onTap: () {
            Navigator.of(context).pop(calendar);
          },
        );
      },
    );
  }
}
