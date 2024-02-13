import 'package:flutter/material.dart';
import 'package:get_it/get_it.dart';
import 'package:go_router/go_router.dart';
import 'package:syncademic_app/new_sync_profile_page.dart';
import 'package:syncademic_app/repository/sync_profile_repository.dart';
import 'package:syncademic_app/widgets/sync_profiles_list.dart';

void main() {
  final getIt = GetIt.instance;

  // Register the SyncProfileRepository
  getIt.registerSingleton<SyncProfileRepository>(
      MockSyncProfileRepository()..createRandomData(10));

  runApp(const MyApp());
}

// GoRouter configuration
final _router = GoRouter(
  routes: [
    GoRoute(
      path: '/',
      builder: (context, state) => const HomeScreen(),
    ),
    GoRoute(
        path: '/new-sync-profile',
        builder: (context, state) {
          return const NewSyncConfigPage();
        }),
  ],
);

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
        title: 'Syncademia',
        theme: ThemeData(
          colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
          useMaterial3: true,
        ),
        routerConfig: _router);
  }
}

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Syncademia'),
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


// Add a "New synchronization profile" button to the HomeScreen