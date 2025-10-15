import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:get_it/get_it.dart';
import 'package:http/http.dart' as http;

import '../../services/auth_service.dart';

class DevToolsPage extends StatefulWidget {
  const DevToolsPage({super.key});

  @override
  State<DevToolsPage> createState() => _DevToolsPageState();
}

class _DevToolsPageState extends State<DevToolsPage> {
  String? _idToken;
  bool _loadingToken = false;
  bool _callingEndpoint = false;
  String? _endpointResponse;
  String? _error;
  Uri? _secureEndpointUri;
  String? _secureEndpointConfigError;

  @override
  void initState() {
    super.initState();
    _applyEndpointConfig();
    _loadIdToken();
  }

  @override
  void reassemble() {
    super.reassemble();
    _applyEndpointConfig(notify: true);
  }

  void _applyEndpointConfig({bool notify = false}) {
    final config = _computeSecureEndpointUri();

    if (notify && mounted) {
      setState(() {
        _secureEndpointUri = config.uri;
        _secureEndpointConfigError = config.error;
      });
    } else {
      _secureEndpointUri = config.uri;
      _secureEndpointConfigError = config.error;
    }
  }

  _SecureEndpointConfig _computeSecureEndpointUri() {
    final base = dotenv.env['FASTAPI_BASE_URL'];
    if (base == null) {
      return const _SecureEndpointConfig(
        error:
            'FASTAPI_BASE_URL is not defined in dotenv. Add it to point the app at your FastAPI server (e.g. http://127.0.0.1:8000).',
      );
    }

    final trimmed = base.trim();
    if (trimmed.isEmpty) {
      return const _SecureEndpointConfig(
        error:
            'FASTAPI_BASE_URL is set but empty. Provide a full base URL such as http://127.0.0.1:8000.',
      );
    }

    try {
      final baseUri = Uri.parse(trimmed);

      if (!baseUri.hasScheme) {
        return _SecureEndpointConfig(
          error:
              'FASTAPI_BASE_URL "$trimmed" is missing a scheme. Include http:// or https://.',
        );
      }

      if (!baseUri.hasAuthority) {
        return _SecureEndpointConfig(
          error:
              'FASTAPI_BASE_URL "$trimmed" is missing a host. Expected something like http://127.0.0.1:8000.',
        );
      }

      return _SecureEndpointConfig(uri: baseUri.resolve('/secure'));
    } on FormatException catch (e) {
      return _SecureEndpointConfig(
        error: 'FASTAPI_BASE_URL "$trimmed" could not be parsed: ${e.message}.',
      );
    }
  }

  Future<void> _loadIdToken({bool forceRefresh = false}) async {
    setState(() {
      _loadingToken = true;
    });

    final token =
        await GetIt.I<AuthService>().getIdToken(forceRefresh: forceRefresh);

    if (!mounted) {
      return;
    }

    setState(() {
      _idToken = token;
      _loadingToken = false;
    });
  }

  Future<void> _callSecureEndpoint() async {
    _applyEndpointConfig(notify: true);

    setState(() {
      _callingEndpoint = true;
      _endpointResponse = null;
      _error = null;
    });

    if (_secureEndpointUri == null) {
      setState(() {
        _callingEndpoint = false;
        _error = _secureEndpointConfigError ??
            'FASTAPI_BASE_URL is missing or invalid. Update the dotenv file to point to your FastAPI instance.';
      });
      return;
    }

    final token = _idToken ?? await GetIt.I<AuthService>().getIdToken();
    if (token == null) {
      setState(() {
        _callingEndpoint = false;
        _error = 'No Firebase ID token available. Sign in first.';
      });
      return;
    }

    try {
      final response = await http.get(
        _secureEndpointUri!,
        headers: {'Authorization': 'Bearer $token'},
      );

      final responseBody = response.body;
      final formattedBody = _formatResponseBody(responseBody);

      setState(() {
        _callingEndpoint = false;
        if (response.statusCode >= 200 && response.statusCode < 300) {
          _endpointResponse = formattedBody;
        } else {
          _error =
              'Request failed with status ${response.statusCode}:\n$formattedBody';
        }
      });
    } catch (e) {
      setState(() {
        _callingEndpoint = false;
        _error = 'Request error: $e';
      });
    }
  }

  String _formatResponseBody(String rawBody) {
    try {
      final decoded = jsonDecode(rawBody);
      const encoder = JsonEncoder.withIndent('  ');
      return encoder.convert(decoded);
    } catch (_) {
      return rawBody;
    }
  }

  @override
  Widget build(BuildContext context) {
    if (!kDebugMode) {
      return const Scaffold(
        body: Center(
          child: Text('Dev tools are only available in debug builds.'),
        ),
      );
    }

    final user = GetIt.I<AuthService>().currentUser;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Developer Tools'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: ListView(
          children: [
            Text(
              'Signed in as: ${user?.email ?? user?.id ?? 'Not signed in'}',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 16),
            Text('FastAPI secure endpoint:'),
            const SizedBox(height: 4),
            SelectableText(
              _secureEndpointUri?.toString() ??
                  _secureEndpointConfigError ??
                  'Not configured',
              style: Theme.of(context).textTheme.bodySmall,
            ),
            const SizedBox(height: 16),
            Text(
              'Firebase ID token (preview):',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 4),
            _loadingToken
                ? const LinearProgressIndicator()
                : SelectableText(
                    _previewToken(_idToken),
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                ElevatedButton.icon(
                  onPressed: _loadingToken
                      ? null
                      : () => _loadIdToken(forceRefresh: true),
                  icon: const Icon(Icons.refresh),
                  label: const Text('Refresh token'),
                ),
                ElevatedButton.icon(
                  onPressed:
                      _callingEndpoint ? null : () => _callSecureEndpoint(),
                  icon: const Icon(Icons.lock),
                  label: const Text('Call /secure'),
                ),
              ],
            ),
            const SizedBox(height: 24),
            if (_callingEndpoint) const LinearProgressIndicator(),
            if (_endpointResponse != null) ...[
              Text(
                'Response',
                style: Theme.of(context).textTheme.titleMedium,
              ),
              const SizedBox(height: 8),
              SelectableText(
                _endpointResponse!,
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ],
            if (_error != null) ...[
              Text(
                'Error',
                style: Theme.of(context)
                    .textTheme
                    .titleMedium
                    ?.copyWith(color: Theme.of(context).colorScheme.error),
              ),
              const SizedBox(height: 8),
              SelectableText(
                _error!,
                style: Theme.of(context)
                    .textTheme
                    .bodySmall
                    ?.copyWith(color: Theme.of(context).colorScheme.error),
              ),
            ],
          ],
        ),
      ),
    );
  }

  String _previewToken(String? token) {
    if (token == null || token.isEmpty) {
      return 'No token loaded';
    }

    if (token.length <= 24) {
      return token;
    }

    return '${token.substring(0, 24)}…';
  }
}

class _SecureEndpointConfig {
  const _SecureEndpointConfig({this.uri, this.error});

  final Uri? uri;
  final String? error;
}
