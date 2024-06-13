import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:gap/gap.dart';
import 'package:syncademic_app/widgets/provider_account_card.dart';

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
        //TODO : when going back or forth one step, the error message is shown again. Fix this.
        if (state.providerAccountError != null) {
          ScaffoldMessenger.of(context)
            ..removeCurrentSnackBar()
            ..showSnackBar(SnackBar(
              content: Text(state.providerAccountError!),
              backgroundColor: Colors.red,
            ));
        }
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
          currentStep: state.currentStep.index,
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
              title: Text("Select your Google account"),
              content: ProviderAccountStepContent(),
            ),
            Step(
              title: Text('Grant Syncademic Permissions'),
              content: BackendAuthorizationStepContent(),
            ),
            Step(
              title: Text('Select your Google Calendar'),
              content: Padding(
                padding: EdgeInsets.all(8.0),
                child: TargetCalendarStepContent(),
              ),
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
        return TextFormField(
          decoration: InputDecoration(
            border: const OutlineInputBorder(),
            hintText: 'INSA Lyon - 2023-2024',
            errorText: state.titleError,
          ),
          initialValue: state.title,
          maxLength: 50,
          onChanged: context.read<NewSyncProfileCubit>().titleChanged,
          onEditingComplete: context.read<NewSyncProfileCubit>().next,
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
        return TextFormField(
          decoration: InputDecoration(
            labelText: 'Calendar url',
            border: const OutlineInputBorder(),
            counterText: '',
            errorText: state.urlError,
          ),
          initialValue: state.url,
          maxLength: 4000,
          onChanged: context.read<NewSyncProfileCubit>().urlChanged,
          onEditingComplete: context.read<NewSyncProfileCubit>().next,
        );
      },
    );
  }
}

class ProviderAccountStepContent extends StatelessWidget {
  const ProviderAccountStepContent({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<NewSyncProfileCubit, NewSyncProfileState>(
      builder: (context, state) {
        //TODO show errors

        if (state.providerAccount == null) {
          return Column(
            children: [
              TextButton(
                onPressed:
                    context.read<NewSyncProfileCubit>().pickProviderAccount,
                child: const Text('Select your Google Account'),
              ),
            ],
          );
        } else {
          return Stack(
            alignment: Alignment.centerRight,
            children: [
              ProviderAccountCard(providerAccount: state.providerAccount!),
              IconButton(
                icon: const Icon(Icons.delete),
                onPressed:
                    context.read<NewSyncProfileCubit>().resetProviderAccount,
              ),
            ],
          );
        }
      },
    );
  }
}

class TargetCalendarStepContent extends StatelessWidget {
  const TargetCalendarStepContent({super.key});

  void _openCalendarSelector(BuildContext context) async {
    final cubit = context.read<NewSyncProfileCubit>();
    final providerAccount = cubit.state.providerAccount;

    if (providerAccount == null) {
      throw StateError(
          'Provider account should not be null when selecting a calendar.');
    }

    final selectedCalendar = await showDialog<TargetCalendar?>(
      context: context,
      builder: (_) => Dialog(
        child: BlocProvider(
          create: (_) => TargetCalendarSelectorCubit(providerAccount)..init(),
          child: const Padding(
            padding: EdgeInsets.all(8.0),
            child: TargetCalendarSelector(),
          ),
        ),
      ),
    );
    cubit.selectExistingCalendar(selectedCalendar);
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
        return Column(
          children: [
            //TODO: add info box
            SegmentedButton<TargetCalendarChoice>(
              onSelectionChanged: context
                  .read<NewSyncProfileCubit>()
                  .targetCalendarChoiceChanged,
              multiSelectionEnabled: false,
              style: SegmentedButton.styleFrom(
                alignment: Alignment.center,
              ),
              segments: const [
                ButtonSegment(
                    value: TargetCalendarChoice.createNew,
                    label: Text(
                      'New calendar',
                      textAlign: TextAlign.center,
                    )),
                ButtonSegment(
                    value: TargetCalendarChoice.useExisting,
                    label: Text(
                      'Select existing',
                      textAlign: TextAlign.center,
                    )),
              ],
              selected: {state.targetCalendarChoice},
            ),
            const Gap(32),

            if (state.targetCalendarSelected != null) ...[
              //TODO extract widget
              Align(
                alignment: Alignment.centerLeft,
                child: Text(
                  state.targetCalendarChoice == TargetCalendarChoice.createNew
                      ? 'Google Calendar to be created :'
                      : 'Your selected calendar :',
                  style: Theme.of(context).textTheme.titleMedium,
                ),
              ),
              const Gap(8),
              TargetCalendarCard(
                targetCalendar: state.targetCalendarSelected!,
                onPressed: state.targetCalendarChoice ==
                        TargetCalendarChoice.useExisting
                    ? () => _openCalendarSelector(context)
                    : null,
                showEditIcon: state.targetCalendarChoice ==
                    TargetCalendarChoice.useExisting,
              ),
            ],
            if (state.existingCalendarSelected == null &&
                state.targetCalendarChoice == TargetCalendarChoice.useExisting)
              ElevatedButton.icon(
                icon: const Icon(Icons.calendar_month),
                onPressed: () => _openCalendarSelector(context),
                label: const Text('Select target calendar'),
              ),
          ],
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
                    Text(
                      state.targetCalendarSelected?.title ??
                          'No calendar selected',
                    ),
                    Text(
                      state.targetCalendarChoice ==
                              TargetCalendarChoice.createNew
                          ? 'This calendar will be created'
                          : 'This calendar already exists',
                    )
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
