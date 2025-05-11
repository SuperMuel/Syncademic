import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:get_it/get_it.dart';
import 'package:go_router/go_router.dart';
import 'package:url_launcher/url_launcher.dart';

import '../../authentication/cubit/auth_cubit.dart';
import '../../services/auth_service.dart';

/// Creates a mailto: URL for deleting an account.
///
/// The email is hardcoded to "info@syncademic.io" and the subject is "Account Deletion Request".
/// The body is a pre-written dramatic message that explains the user's reason for deleting their account.
String _getAccountDeletionMailto(String accountId) {
  return "mailto:info@syncademic.io?subject=Account%20Deletion%20Request&body=Dear%20Syncademic%20Team%2C%0A%0AIt%20is%20with%20a%20heavy%20heart%20that%20I%20write%20this.%20Syncademic%20has%20truly%20transformed%20my%20academic%20life%2C%20and%20your%20service%20has%20been%20nothing%20short%20of%20extraordinary.%20However%2C%20despite%20my%20deep%20appreciation%2C%20circumstances%20compel%20me%20to%20part%20ways.%0A%0AI%20kindly%20ask%20you%20to%20delete%20my%20account%20associated%20with%20the%20following%20ID%3A%20$accountId.%0A%0AKnow%20that%20this%20decision%20does%20not%20reflect%20dissatisfaction%20but%20rather%20a%20personal%20journey%20I%20must%20undertake.%20I%20will%20always%20remember%20Syncademic%20fondly.%0A%0AWith%20gratitude%2C%20%20%0A%5BYour%20Name%5D";
}

class IdTokenWidget extends StatefulWidget {
  const IdTokenWidget({super.key});

  @override
  State<IdTokenWidget> createState() => _IdTokenWidgetState();
}

class _IdTokenWidgetState extends State<IdTokenWidget> {
  String? _idToken;
  bool _isLoadingToken = false;

  @override
  void initState() {
    super.initState();
    _loadIdToken();
  }

  Future<void> _loadIdToken() async {
    setState(() {
      _isLoadingToken = true;
    });

    final token = await GetIt.I<AuthService>().getIdToken();

    setState(() {
      _idToken = token;
      _isLoadingToken = false;
    });
  }

  Future<void> _refreshIdToken() async {
    setState(() {
      _isLoadingToken = true;
    });

    final token = await GetIt.I<AuthService>().getIdToken(forceRefresh: true);

    setState(() {
      _idToken = token;
      _isLoadingToken = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(
          "Firebase ID Token",
          style: Theme.of(context).textTheme.titleMedium,
        ),
        const SizedBox(height: 10),
        if (_isLoadingToken)
          const CircularProgressIndicator()
        else if (_idToken != null)
          Column(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  border: Border.all(color: Colors.grey),
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Row(
                  children: [
                    Expanded(
                      child: SelectableText(
                        _idToken!,
                        style: const TextStyle(
                          fontFamily: 'monospace',
                          fontSize: 12,
                        ),
                      ),
                    ),
                    IconButton(
                      icon: const Icon(Icons.copy),
                      onPressed: () {
                        Clipboard.setData(ClipboardData(text: _idToken!));
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(
                            content: Text('Copied to clipboard'),
                            duration: Duration(seconds: 1),
                          ),
                        );
                      },
                      tooltip: "Copy to clipboard",
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 10),
              ElevatedButton.icon(
                onPressed: _refreshIdToken,
                icon: const Icon(Icons.refresh),
                label: const Text('Refresh Token'),
              ),
              const SizedBox(height: 10),
            ],
          )
        else
          const Text("Unable to retrieve token"),
      ],
    );
  }
}

class AccountPage extends StatefulWidget {
  const AccountPage({super.key});

  @override
  State<AccountPage> createState() => _AccountPageState();
}

class _AccountPageState extends State<AccountPage> {
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
                          "To delete your account, you'll need to send an email to info@syncademic.io. We'll process the deletion after receiving your request."),
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
            child: SingleChildScrollView(
              child: Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: <Widget>[
                    Text(
                      "We don't have too much information about you...",
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
                              text: "You signed up for Syncademic using your ",
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
                            "Note that you can also synchronize your school schedule with other Google accounts without creating a new Syncademic account.",
                            style: Theme.of(context).textTheme.bodyMedium,
                          ),
                          const SizedBox(height: 40),
                          if (kDebugMode) ...[
                            const Divider(),
                            const SizedBox(height: 20),
                            const IdTokenWidget(),
                          ],
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        );
      },
    );
  }
}
