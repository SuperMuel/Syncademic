import 'package:cloud_functions/cloud_functions.dart';
import 'package:feedback_sentry/feedback_sentry.dart';
import 'package:firebase_app_check/firebase_app_check.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:gap/gap.dart';
import 'package:get_it/get_it.dart';
import 'package:go_router/go_router.dart';
import 'package:google_sign_in/google_sign_in.dart';
import 'package:googleapis/calendar/v3.dart' show CalendarApi;
import 'package:package_info_plus/package_info_plus.dart';
import 'package:sentry_flutter/sentry_flutter.dart';
import 'package:url_launcher/url_launcher.dart';

import 'authentication/cubit/auth_cubit.dart';
import 'authorization/authorization_service.dart';
import 'authorization/backend_authorization_service.dart';
import 'authorization/firebase_backend_authorization_service.dart';
import 'authorization/google_authorization/google_authorization_service.dart';
import 'firebase_options.dart';
import 'repositories/firestore_sync_profile_repository.dart';
import 'repositories/google_target_calendar_repository.dart';
import 'repositories/sync_profile_repository.dart';
import 'repositories/target_calendar_repository.dart';
import 'screens/account/account_page.dart';
import 'screens/new_sync_profile/cubit/new_sync_profile_cubit.dart';
import 'screens/new_sync_profile/new_sync_profile_page.dart';
import 'screens/sign_in_page.dart';
import 'screens/sync_profile/cubit/sync_profile_cubit.dart';
import 'screens/sync_profile/sync_profile_page.dart';
import 'services/account_service.dart';
import 'services/api_client.dart'; // Added ApiClient import
import 'services/auth_service.dart';
import 'services/firebase_auth_service.dart';
import 'services/firebase_sync_profile_service.dart';
import 'services/firestore_account_service.dart';
import 'services/ics_validation_service.dart';
import 'services/provider_account_service.dart';
import 'services/sync_profile_service.dart';
import 'widgets/feedback_icon_button.dart';
import 'widgets/sync_profiles_list.dart';

void registerDependencies() {
  final getIt = GetIt.instance;

  // Retrieve FastAPI base URL
  final fastApiBaseUrl = dotenv.env['FASTAPI_BASE_URL'];
  if (fastApiBaseUrl == null || fastApiBaseUrl.isEmpty) {
    // In a real app, you might want to log this error or handle it more gracefully.
    // For this setup, throwing an error during startup is acceptable if the URL is critical.
    throw StateError('FASTAPI_BASE_URL is not set in the environment variables.');
  }

  // Create and register ApiClient
  final apiClient = ApiClient(baseUrl: fastApiBaseUrl);
  getIt.registerSingleton<ApiClient>(apiClient);


  final googleSignIn = GoogleSignIn(
    clientId: dotenv.env['SYNCADEMIC_CLIENT_ID'],
    forceCodeForRefreshToken: true,
    scopes: [CalendarApi.calendarScope],
  );

  final functions = FirebaseFunctions.instanceFor(
      region: dotenv.env['FIREBASE_FUNCTIONS_REGION']);

  getIt.registerSingleton<FirebaseFunctions>(functions);

  getIt.registerSingleton<SyncProfileRepository>(
    FirestoreSyncProfileRepository(),
  );

  getIt.registerSingleton<AuthService>(
    FirebaseAuthService(),
  );

  getIt.registerSingleton<AuthCubit>(AuthCubit());

  getIt.registerSingleton<AccountService>(FirebaseAccountService());

  getIt.registerSingleton<AuthorizationService>(
    GoogleAuthorizationService(googleSignIn: googleSignIn),
  );

  // Updated FirebaseSyncProfileService registration
  getIt.registerSingleton<SyncProfileService>(
    FirebaseSyncProfileService(
      functions: functions, // Explicitly pass if still needed, or let GetIt resolve if registered
      apiClient: getIt<ApiClient>(),
    ),
  );

  getIt.registerSingleton<BackendAuthorizationService>(
    FirebaseBackendAuthorizationService(
      redirectUri: dotenv
          .env[kDebugMode ? 'LOCAL_REDIRECT_URI' : 'PRODUCTION_REDIRECT_URI']!,
    ),
  );

  getIt.registerSingleton<TargetCalendarRepository>(
    GoogleTargetCalendarRepository(),
  );

  getIt.registerSingleton<ProviderAccountService>(
    GoogleProviderAccountService(googleSignIn: googleSignIn),
  );

  // Updated FirebaseIcsValidationService registration
  getIt.registerSingleton<IcsValidationService>(
    FirebaseIcsValidationService(
      functions: functions, // Explicitly pass if still needed
      apiClient: getIt<ApiClient>(),
    ),
  );
}

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await dotenv.load(fileName: "dotenv");

  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );

  if (dotenv.env['RECAPTCHA_V3_SITE_KEY'] == null) {
    throw Exception('RECAPTCHA_V3_SITE_KEY environment variable is not set.');
  }

  await FirebaseAppCheck.instance.activate(
    webProvider: ReCaptchaV3Provider(dotenv.env['RECAPTCHA_V3_SITE_KEY']!),
    androidProvider: AndroidProvider.debug,
    appleProvider: AppleProvider.debug,
  );

  registerDependencies(); // Call after dotenv.load and before services are used

  await SentryFlutter.init(
    (options) {
      options.dsn = dotenv.env['SENTRY_DSN'];
      options.tracesSampleRate = 1.0;
      options.profilesSampleRate = 1.0;
    },
    appRunner: () => runApp(
      const BetterFeedback(child: MyApp()),
    ),
  );
}

// GoRouter configuration
final _router = GoRouter(
  redirect: (context, state) async {
    final user = GetIt.I<AuthService>().currentUser;

    if (user == null) {
      return '/sign-in';
    }

    if (state.fullPath == '/sign-in') {
      return '/';
    }

    return null;
  },
  initialLocation: '/sign-in',
  routes: [
    GoRoute(
      path: '/sign-in',
      builder: (context, state) => const SignInPage(),
    ),
    GoRoute(
        path: '/',
        builder: (context, state) => const HomeScreen(),
        routes: [
          GoRoute(
            path: 'syncProfile/:id',
            builder: (context, state) => BlocProvider(
              create: (context) =>
                  SyncProfileCubit(state.pathParameters['id'] ?? ''),
              child: const SyncProfilePage(),
            ),
          ),
        ]),
    GoRoute(
        path: '/account',
        builder: (context, state) {
          return const AccountPage();
        }),
    GoRoute(
        path: '/new-sync-profile',
        builder: (_, __) {
          return BlocProvider(
            create: (_) => NewSyncProfileCubit(),
            child: const NewSyncProfilePage(),
          );
        }),
  ],
);

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: 'Syncademic',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
        useMaterial3: true,
      ),
      routerConfig: _router,
    );
  }
}

class _HomeScreenState extends State<HomeScreen> {
  PackageInfo? packageInfo;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Syncademic'),
        actions: [
          IconButton(
            icon: const Icon(Icons.info),
            onPressed: () => showAboutDialog(
                context: context,
                applicationIcon: SvgPicture.asset(
                  'assets/icons/syncademic-icon.svg',
                  semanticsLabel: 'Syncademic logo',
                  width: 40,
                ),
                applicationName: 'Syncademic',
                applicationVersion: packageInfo?.version,
                applicationLegalese: '© 2024 Syncademic',
                children: [
                  const Gap(10),
                  Center(
                    child: GestureDetector(
                      onTap: () async {
                        const urlString =
                            'https://github.com/supermuel/syncademic';
                        await launchUrl(Uri.parse(urlString));
                      },
                      child: const Text.rich(
                        TextSpan(
                          text: 'Made by ',
                          children: [
                            TextSpan(
                              text: 'SuperMuel',
                              style: TextStyle(
                                color: Colors.blue,
                                decoration: TextDecoration.underline,
                              ),
                            ),
                            TextSpan(
                              text: ' 🤗',
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ]),
            tooltip: "About",
          ),
          IconButton(
            icon: const Icon(Icons.account_circle),
            onPressed: () => context.push('/account'),
            tooltip: "Account",
          ),
          const FeedbackIconButton(),
        ],
      ),
      body: SafeArea(
        child: SyncProfilesList(
          onTap: (profile) => context.go('/syncProfile/${profile.id.value}'),
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        icon: const Icon(Icons.add),
        onPressed: () {
          context.push('/new-sync-profile');
        },
        label: const Text('New Synchronization'),
      ),
    );
  }

  @override
  void initState() {
    super.initState();
    PackageInfo.fromPlatform().then((value) => setState(() {
          packageInfo = value;
        }));
  }
}
