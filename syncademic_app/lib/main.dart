import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:get_it/get_it.dart';
import 'package:go_router/go_router.dart';
import 'package:syncademic_app/authentication/cubit/auth_cubit.dart';
import 'services/auth_service.dart';

import 'firebase_options.dart';
import 'repositories/sync_profile_repository.dart';
import 'screens/google_sign_in_page/google_sign_in_page.dart';
import 'screens/new_sync_profile/new_sync_profile_cubit.dart';
import 'screens/new_sync_profile/new_sync_profile_page.dart';
import 'widgets/sync_profiles_list.dart';

void main() async {
  final getIt = GetIt.instance;

  WidgetsFlutterBinding.ensureInitialized();

  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );

  // Register the SyncProfileRepository
  getIt.registerSingleton<SyncProfileRepository>(
      MockSyncProfileRepository()..createRandomData(10));

  getIt.registerSingleton<AuthService>(MockAuthService());

  getIt.registerSingleton<AuthCubit>(AuthCubit());

  runApp(const MyApp());
}

// GoRouter configuration
final _router = GoRouter(
  redirect: (context, state) async {
    final user = await GetIt.I<AuthService>().currentUser;
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
        builder: (context, state) => const GoogleSignInPage()),
    GoRoute(
        path: '/new-sync-profile',
        builder: (_, __) {
          return BlocProvider(
            create: (_) => NewSyncProfileCubit(),
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
      title: 'Syncademia',
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
        title: const Text('Syncademia'),
        actions: [
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
