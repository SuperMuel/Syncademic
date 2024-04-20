import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:gap/gap.dart';

import '../../models/target_calendar.dart';
import '../../widgets/target_calendar_card.dart';
import 'cubit/new_sync_profile_cubit.dart';
import 'target_calendar_selector/target_calendar_selector.dart';
import 'target_calendar_selector/target_calendar_selector_cubit.dart';

class NewSyncProfilePage extends StatelessWidget {
  const NewSyncProfilePage({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocConsumer<NewSyncProfileCubit, NewSyncProfileState>(
      listener: (context, state) {
        if (state.submittedSuccessfully) {
          Navigator.of(context).pop();
          ScaffoldMessenger.of(context)
            ..removeCurrentSnackBar()
            ..showSnackBar(const SnackBar(
              content: Text('Synchronization created'),
              backgroundColor: Colors.green,
            ));
          return;
        }

        if (state.submitError != null) {
          ScaffoldMessenger.of(context)
            ..removeCurrentSnackBar()
            ..showSnackBar(SnackBar(
              content: Text('Error: ${state.submitError}'),
              backgroundColor: Colors.red,
            ));
        }
      },
      builder: (context, state) => Scaffold(
        appBar: AppBar(
          title: const Text('New synchronization'),
        ),
        body: Stepper(
          currentStep: state.currentStep,
          onStepContinue: state.canContinue
              ? context.read<NewSyncProfileCubit>().next
              : null,
          onStepCancel: state.canGoBack
              ? context.read<NewSyncProfileCubit>().previous
              : null,
          steps: const [
            Step(
              title: Text('Give a title to your synchronization'),
              content: Padding(
                padding: EdgeInsets.all(8.0),
                child: TitleStepContent(),
              ),
            ),
            Step(
              title: Text('Provide your time schedule url'),
              content: Padding(
                padding: EdgeInsets.all(8.0),
                child: UrlStepContent(),
              ),
            ),
            Step(
              title: Text('Select your Google Calendar'),
              content: Padding(
                padding: EdgeInsets.all(8.0),
                child: TargetCalendarStepContent(),
              ),
            ),
            Step(
              title: Text('Grant Syncademic Permissions'),
              content: BackendAuthorizationStepContent(),
            ),
            Step(
              title: Text('Summary'),
              content: SummaryStepContent(),
            )
          ],
        ),
      ),
    );
  }
}

class TitleStepContent extends StatelessWidget {
  const TitleStepContent({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<NewSyncProfileCubit, NewSyncProfileState>(
      builder: (context, state) {
        return TextField(
          decoration: InputDecoration(
            border: const OutlineInputBorder(),
            hintText: 'INSA Lyon - 2023-2024',
            errorText: state.titleError,
          ),
          maxLength: 50,
          onChanged: context.read<NewSyncProfileCubit>().titleChanged,
        );
      },
    );
  }
}

class UrlStepContent extends StatelessWidget {
  const UrlStepContent({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<NewSyncProfileCubit, NewSyncProfileState>(
      builder: (context, state) {
        return TextField(
          decoration: InputDecoration(
            labelText: 'Calendar url',
            border: const OutlineInputBorder(),
            counterText: '',
            errorText: state.urlError,
          ),
          maxLength: 4000,
          onChanged: context.read<NewSyncProfileCubit>().urlChanged,
        );
      },
    );
  }
}

class TargetCalendarStepContent extends StatelessWidget {
  const TargetCalendarStepContent({super.key});

  void _openCalendarSelector(BuildContext context) async {
    final cubit = context.read<NewSyncProfileCubit>();
    final selectedCalendar = await showDialog<TargetCalendar?>(
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
    );
    cubit.selectCalendar(selectedCalendar);
  }

  @override
  Widget build(BuildContext context) {
    //TODO : add explanations about what the calendar is used for
    return BlocConsumer<NewSyncProfileCubit, NewSyncProfileState>(
      listener: (context, state) {
        if (state.backendAuthorizationError != null) {
          ScaffoldMessenger.of(context)
            ..removeCurrentSnackBar()
            ..showSnackBar(SnackBar(
              content: Text('Error: ${state.backendAuthorizationError}'),
              backgroundColor: Colors.red,
            ));
        }
      },
      builder: (context, state) {
        return state.targetCalendar == null
            ? ElevatedButton.icon(
                icon: const Icon(Icons.calendar_month),
                onPressed: () => _openCalendarSelector(context),
                label: const Text('Select target calendar'),
              )
            : TargetCalendarCard(
                targetCalendar: state.targetCalendar!,
                onPressed: () => _openCalendarSelector(context),
              );
      },
    );
  }
}

class BackendAuthorizationStepContent extends StatelessWidget {
  const BackendAuthorizationStepContent({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<NewSyncProfileCubit, NewSyncProfileState>(
      builder: (context, state) {
        return Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'To synchronize your schedule, Syncademic needs to access your Google Calendar.',
              ),
              const Gap(16),
              state.hasAuthorizedBackend
                  ? const Row(
                      children: [
                        Icon(Icons.check_circle, color: Colors.green),
                        Gap(8),
                        Text('Authorization successful'),
                      ],
                    )
                  : ElevatedButton.icon(
                      style: ElevatedButton.styleFrom(
                          padding: const EdgeInsets.all(24.0)),
                      onPressed: state.isAuthorizingBackend
                          ? null
                          : context
                              .read<NewSyncProfileCubit>()
                              .authorizeBackend,
                      icon: state.isAuthorizingBackend
                          ? const CircularProgressIndicator(strokeWidth: 2)
                          : const Icon(Icons.lock_open),
                      label: Text(
                        'Authorize Syncademic',
                        style: Theme.of(context).textTheme.bodyLarge,
                      ),
                    ),
            ],
          ),
        );
      },
    );
  }
}

class SummaryStepContent extends StatelessWidget {
  const SummaryStepContent({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<NewSyncProfileCubit, NewSyncProfileState>(
      builder: (context, state) {
        return Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Synchronization title :',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    const Gap(8),
                    Text(state.title),
                    const Gap(16),
                    Text(
                      'Time schedule URL :',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    const Gap(8),
                    Text(state.url),
                    const Gap(16),
                    Text(
                      'Google Calendar :',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    const Gap(8),
                    Text(state.targetCalendar?.title ?? 'Not selected'),
                  ],
                ),
              ),
              const Gap(24),
              ElevatedButton.icon(
                style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.all(24.0)),
                onPressed: state.isSubmitting
                    ? null
                    : context.read<NewSyncProfileCubit>().submit,
                icon: state.isSubmitting
                    ? const CircularProgressIndicator(strokeWidth: 2)
                    : const Icon(Icons.check),
                label: Text(
                  'Create synchronization',
                  style: Theme.of(context).textTheme.bodyLarge,
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}
