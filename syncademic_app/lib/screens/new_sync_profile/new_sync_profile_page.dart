import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:gap/gap.dart';
import 'package:syncademic_app/screens/new_sync_profile/stepper_cubit/stepper_cubit.dart';
import '../../models/target_calendar.dart';
import 'target_calendar_selector/target_calendar_selector_cubit.dart';
import '../../widgets/target_calendar_card.dart';
import 'target_calendar_selector/target_calendar_selector.dart';

class NewSyncProfilePage extends StatelessWidget {
  const NewSyncProfilePage({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocConsumer<StepperCubit, StepperState>(
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
          onStepContinue:
              state.canContinue ? context.read<StepperCubit>().next : null,
          onStepCancel:
              state.canGoBack ? context.read<StepperCubit>().previous : null,
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
    return BlocBuilder<StepperCubit, StepperState>(
      builder: (context, state) {
        return TextField(
          decoration: InputDecoration(
            labelText: 'Title',
            border: const OutlineInputBorder(),
            hintText: 'L3 - Biologie - 2023-2024',
            errorText: state.titleError,
          ),
          maxLength: 50,
          onChanged: context.read<StepperCubit>().titleChanged,
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
    return BlocBuilder<StepperCubit, StepperState>(
      builder: (context, state) {
        return TextField(
          decoration: InputDecoration(
            labelText: 'Calendar url',
            border: const OutlineInputBorder(),
            counterText: '',
            errorText: state.urlError,
          ),
          maxLength: 4000,
          onChanged: context.read<StepperCubit>().urlChanged,
        );
      },
    );
  }
}

class TargetCalendarStepContent extends StatelessWidget {
  const TargetCalendarStepContent({super.key});

  void _onPressed(BuildContext context) async {
    final cubit = context.read<StepperCubit>();
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
    return BlocBuilder<StepperCubit, StepperState>(
      builder: (context, state) {
        return state.targetCalendar == null
            ? ElevatedButton.icon(
                icon: const Icon(Icons.calendar_month),
                onPressed: () => _onPressed(context),
                label: const Text('Select target calendar'),
              )
            : TargetCalendarCard(
                targetCalendar: state.targetCalendar!,
                onPressed: () => _onPressed(context),
              );
      },
    );
  }
}

class BackendAuthorizationStepContent extends StatelessWidget {
  const BackendAuthorizationStepContent({super.key});

  @override
  Widget build(BuildContext context) {
    return const Placeholder();
  }
}

class SummaryStepContent extends StatelessWidget {
  const SummaryStepContent({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<StepperCubit, StepperState>(
      builder: (context, state) {
        return Column(
          children: [
            Text('Title: ${state.title}'),
            const Gap(8),
            Text('URL: ${state.url}'),
            const Gap(8),
            Text('Calendar: ${state.targetCalendar?.title ?? 'Not selected'}'),
            const Gap(8),
            ElevatedButton(
              onPressed: context.read<StepperCubit>().submit,
              child: const Text('Submit'),
            ),
            if (state.isSubmitting) const CircularProgressIndicator()
          ],
        );
      },
    );
  }
}
