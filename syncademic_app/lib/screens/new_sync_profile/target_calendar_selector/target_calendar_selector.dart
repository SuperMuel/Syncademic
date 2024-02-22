import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import 'target_calendar_selector_cubit.dart';

class TargetCalendarSelector extends StatelessWidget {
  const TargetCalendarSelector({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<TargetCalendarSelectorCubit,
        TargetCalendarSelectorState>(
      builder: (context, state) {
        return state.when(
          unauthorized: () => const _UnauthorizedBody(),
          authorizing: () => const Center(
            child: CircularProgressIndicator(),
          ),
          authorized: () => const Text('Authorized'),
        );
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
