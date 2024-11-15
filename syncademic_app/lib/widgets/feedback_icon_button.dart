import 'package:feedback_sentry/feedback_sentry.dart';
import 'package:flutter/material.dart';
import 'package:get_it/get_it.dart';

import '../services/auth_service.dart';

class FeedbackIconButton extends StatelessWidget {
  const FeedbackIconButton({super.key});

  @override
  Widget build(BuildContext context) => IconButton(
        icon: const Icon(Icons.feedback),
        onPressed: () {
          final currentUser = GetIt.I<AuthService>().currentUser;
          BetterFeedback.of(context).showAndUploadToSentry(
            email: currentUser?.email,
            name: currentUser?.displayName,
          );
        },
        tooltip: "Feedback",
      );
}
