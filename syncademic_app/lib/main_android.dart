import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:get_it/get_it.dart';
import 'package:go_router/go_router.dart';
import 'package:syncademic_app/firebase_options.dart';
import 'package:syncademic_app/services/firebase_auth_service.dart';
import 'authentication/cubit/auth_cubit.dart';
import 'authorization/authorization_service.dart';
import 'authorization/backend_authorization_service.dart';
import 'repositories/sync_profile_repository.dart';
import 'repositories/target_calendar_repository.dart';
import 'screens/account/account_page.dart';
import 'screens/landing_page.dart';
import 'screens/new_sync_profile/cubit/new_sync_profile_cubit.dart';
import 'screens/new_sync_profile/new_sync_profile_page.dart';
import 'screens/new_sync_profile/target_calendar_selector/target_calendar_selector_cubit.dart';
import 'screens/sync_profile/cubit/sync_profile_cubit.dart';
import 'screens/sync_profile/sync_profile_page.dart';
import 'services/auth_service.dart';
import 'services/sync_profile_service.dart';
import 'widgets/sync_profiles_list.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );

  final getIt = GetIt.instance;
  getIt.registerSingleton<AuthService>(
    FirebaseAuthService(),
    //MockAuthService(),
  );

  getIt.registerSingleton<AuthCubit>(AuthCubit());

  getIt.registerSingleton<SyncProfileService>(
    //FirebaseSyncProfileService(),
    MockSyncProfileService(),
  );
  getIt.registerSingleton<SyncProfileRepository>(
    // FirestoreSyncProfileRepository(),
    MockSyncProfileRepository()
      ..createRandomData(10)
      ..addFailedProfile()
      ..addInProgressProfile(),
  );
  getIt.registerSingleton<BackendAuthorizationService>(
    //FirebaseBackendAuthorizationService(),
    MockBackendAuthorizationService(),
  );

  getIt.registerSingleton<AuthorizationService>(
    MockAuthorizationService(),
  );

  getIt.registerSingleton<TargetCalendarRepository>(
    MockTargetCalendarRepository(),
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

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Syncademic'),
        actions: [
          IconButton(
            icon: const Icon(Icons.account_circle),
            onPressed: () => context.push('/account'),
          ),
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () =>
                GetIt.I<AuthCubit>().signOut().then((_) => context.go('/')),
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
