import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:get_it/get_it.dart';
import 'package:go_router/go_router.dart';
import 'repositories/google_target_calendar_repository.dart';
import 'repositories/target_calendar_repository.dart';
import 'authorization/firebase_backend_authorization_service.dart';
import 'authorization/google_authorization/google_authorization_service.dart';
import 'services/firebase_sync_profile_service.dart';

import 'authentication/cubit/auth_cubit.dart';
import 'authorization/authorization_service.dart';
import 'authorization/backend_authorization_service.dart';
import 'firebase_options.dart';
import 'repositories/firestore_sync_profile_repository.dart';
import 'repositories/sync_profile_repository.dart';
import 'screens/account/account_page.dart';
import 'screens/landing_page.dart';
import 'screens/new_sync_profile/cubit/new_sync_profile_cubit.dart';
import 'screens/new_sync_profile/new_sync_profile_page.dart';
import 'screens/new_sync_profile/target_calendar_selector/target_calendar_selector_cubit.dart';
import 'screens/sync_profile/cubit/sync_profile_cubit.dart';
import 'screens/sync_profile/sync_profile_page.dart';
import 'services/account_service.dart';
import 'services/auth_service.dart';
import 'services/firebase_auth_service.dart';
import 'services/firestore_account_service.dart';
import 'services/sync_profile_service.dart';
import 'widgets/sync_profiles_list.dart';
import 'package:package_info_plus/package_info_plus.dart';

void main() async {
  await dotenv.load(fileName: "dotenv");

  final getIt = GetIt.instance;

  WidgetsFlutterBinding.ensureInitialized();

  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );

  getIt.registerSingleton<SyncProfileRepository>(
    FirestoreSyncProfileRepository(),
    // MockSyncProfileRepository()
    //   ..createRandomData(10)
    //   ..addFailedProfile()
    //   ..addInProgressProfile(),
  );

  getIt.registerSingleton<AuthService>(
    //MockAuthService(),
    FirebaseAuthService(),
  );

  getIt.registerSingleton<AuthCubit>(AuthCubit());

  getIt.registerSingleton<AccountService>(FirebaseAccountService());

  getIt.registerSingleton<AuthorizationService>(
    // MockAuthorizationService(),
    GoogleAuthorizationService(),
  );

  getIt.registerSingleton<SyncProfileService>(FirebaseSyncProfileService());

  getIt.registerSingleton<BackendAuthorizationService>(
    // MockBackendAuthorizationService(),
    //
    // Local :
    // FirebaseBackendAuthorizationService(redirectUri: 'http://localhost:7357'),
    //
    // Production :
    FirebaseBackendAuthorizationService(),
  );

  getIt.registerSingleton<TargetCalendarRepository>(
    //MockTargetCalendarRepository(),
    GoogleTargetCalendarRepository(),
  );

  runApp(const MyApp());
}

// GoRouter configuration
final _router = GoRouter(
  redirect: (context, state) async {
    final user = GetIt.I<AuthService>().currentUser;
    if (user != null) {
      if (state.fullPath == '/welcome') {
        // Logged in users should be redirected to the home screen if they try to access the welcome screen
        return '/';
      }
      return null;
    }

    return '/welcome';
  },
  initialLocation: '/welcome',
  routes: [
    GoRoute(
      path: '/welcome',
      builder: (context, state) => const LandingPage(),
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
    // Account page
    GoRoute(
        path: '/account',
        builder: (context, state) {
          return const AccountPage();
        }),
    GoRoute(
        path: '/new-sync-profile',
        builder: (_, __) {
          return MultiBlocProvider(
            providers: [
              BlocProvider(create: (_) => NewSyncProfileCubit()),
              BlocProvider(create: (_) => TargetCalendarSelectorCubit()),
            ],
            child: const NewSyncProfilePage(),
          );
        }),
  ],
);

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

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  PackageInfo? packageInfo;

  @override
  void initState() {
    super.initState();
    PackageInfo.fromPlatform().then((value) => setState(() {
          packageInfo = value;
        }));
  }

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
            ),
            tooltip: "About",
          ),
          IconButton(
            icon: const Icon(Icons.account_circle),
            onPressed: () => context.push('/account'),
            tooltip: "Account",
          ),
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () =>
                GetIt.I<AuthCubit>().signOut().then((_) => context.go('/')),
            tooltip: "Sign out",
          ),
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
        label: const Text('New synchronization profile'),
      ),
    );
  }
}
