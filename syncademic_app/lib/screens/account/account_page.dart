import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:get_it/get_it.dart';
import 'package:go_router/go_router.dart';
import 'package:url_launcher/url_launcher.dart';

import '../../authentication/cubit/auth_cubit.dart';

/// Creates a mailto: URL for deleting an account.
///
/// The email is hardcoded to "info@syncademic.io" and the subject is "Account Deletion Request".
/// The body is a pre-written dramatic message that explains the user's reason for deleting their account.
String _getAccountDeletionMailto(String accountId) {
  return "mailto:info@syncademic.io?subject=Account%20Deletion%20Request&body=Dear%20Syncademic%20Team%2C%0A%0AIt%20is%20with%20a%20heavy%20heart%20that%20I%20write%20this.%20Syncademic%20has%20truly%20transformed%20my%20academic%20life%2C%20and%20your%20service%20has%20been%20nothing%20short%20of%20extraordinary.%20However%2C%20despite%20my%20deep%20appreciation%2C%20circumstances%20compel%20me%20to%20part%20ways.%0A%0AI%20kindly%20ask%20you%20to%20delete%20my%20account%20associated%20with%20the%20following%20ID%3A%20$accountId.%0A%0AKnow%20that%20this%20decision%20does%20not%20reflect%20dissatisfaction%20but%20rather%20a%20personal%20journey%20I%20must%20undertake.%20I%20will%20always%20remember%20Syncademic%20fondly.%0A%0AWith%20gratitude%2C%20%20%0A%5BYour%20Name%5D";
}

class AccountPage extends StatelessWidget {
  const AccountPage({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<AuthCubit, AuthState>(
      bloc: GetIt.I<AuthCubit>(),
      builder: (context, state) {
        final user = state.maybeMap(
          orElse: () => null,
          authenticated: (user) => user.user,
        );
        if (user == null) {
          return const Center(child: CircularProgressIndicator());
        }

        return Scaffold(
          appBar: AppBar(
            title: const Text('Account'),
            actions: [
              IconButton(
                icon: const Icon(Icons.delete),
                onPressed: () => {
                  showDialog(
                    context: context,
                    builder: (context) => AlertDialog(
                      title: const Text('Delete account'),
                      content: const Text(
                          "To delete your account, you'll have to send an email to info@syncademic.io. We'll delete your account shortly after receiving the email."),
                      actions: [
                        TextButton(
                            onPressed: () => context.pop(),
                            child: const Text('Cancel')),
                        TextButton(
                            onPressed: () {
                              launchUrl(Uri.parse(
                                  _getAccountDeletionMailto(user.id)));
                            },
                            child: const Text('Send pre-written email')),
                      ],
                    ),
                  ),
                },
                tooltip: "Delete account",
              ),
              IconButton(
                icon: const Icon(Icons.logout),
                onPressed: () => GetIt.I<AuthCubit>()
                    .signOut()
                    .then((value) => context.go('/')),
                tooltip: "Sign out",
              ),
            ],
          ),
          body: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: <Widget>[
                  Text(
                    "We don't know much about you...",
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  const SizedBox(height: 20),
                  ConstrainedBox(
                    constraints: BoxConstraints(
                      maxWidth: MediaQuery.of(context).size.width > 500
                          ? 400
                          : double.infinity,
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.center,
                      children: [
                        Text.rich(
                          TextSpan(
                            text:
                                "We can only tell you that you signed up to Syncademic using your ",
                            children: <TextSpan>[
                              TextSpan(
                                text: user.email,
                                style: const TextStyle(
                                    fontWeight: FontWeight.bold,
                                    color: Colors.blue),
                              ),
                              const TextSpan(
                                text: " Google Account.",
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(height: 20),
                        Text(
                          "Note that you can synchronize your school time schedule to other google accounts, without creating another Syncademic account.",
                          style: Theme.of(context).textTheme.bodyMedium,
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }
}
