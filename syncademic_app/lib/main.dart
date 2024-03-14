import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:get_it/get_it.dart';
import 'package:go_router/go_router.dart';

import 'authentication/cubit/auth_cubit.dart';
import 'authorization/authorization_service.dart';
import 'firebase_options.dart';
import 'repositories/firestore_sync_profile_repository.dart';
import 'repositories/sync_profile_repository.dart';
import 'screens/account/account_page.dart';
import 'screens/google_sign_in_page/google_sign_in_page.dart';
import 'screens/new_sync_profile/new_sync_profile_cubit.dart';
import 'screens/new_sync_profile/new_sync_profile_page.dart';
import 'screens/new_sync_profile/target_calendar_selector/target_calendar_selector_cubit.dart';
import 'services/account_service.dart';
import 'services/auth_service.dart';
import 'services/firebase_auth_service.dart';
import 'services/firestore_account_service.dart';
import 'widgets/sync_profiles_list.dart';

void main() async {
  await dotenv.load(fileName: "dotenv");

  final getIt = GetIt.instance;

  WidgetsFlutterBinding.ensureInitialized();

  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );

  // Register the SyncProfileRepository
  getIt.registerSingleton<SyncProfileRepository>(
    FirestoreSyncProfileRepository(),
    // MockSyncProfileRepository()..createRandomData(10),
  );

  getIt.registerSingleton<AuthService>(FirebaseAuthService());

  getIt.registerSingleton<AuthCubit>(AuthCubit());

  getIt.registerSingleton<AccountService>(FirebaseAccountService());

  getIt.registerSingleton<AuthorizationService>(
    //MockAuthorizationService(),
    GoogleAuthorizationService(),
  );

  runApp(const MyApp());
}

// GoRouter configuration
final _router = GoRouter(
  redirect: (context, state) async {
    final user = GetIt.I<AuthService>().currentUser;
    if (user == null) {
      return '/sign-in';
    }
    return null;
  },
  initialLocation: '/',
  routes: [
    GoRoute(
      path: '/',
      builder: (context, state) => const HomeScreen(),
    ),
    GoRoute(
        path: '/sign-in',
        builder: (context, state) {
          return const GoogleSignInPage();
        }),
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
            child: const NewSyncConfigPage(),
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
            onPressed: () => GetIt.I<AuthCubit>()
                .signOut()
                .then((value) => context.go('/sign-in')),
          ),
        ],
      ),
      body: const SyncProfilesList(),
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
