import 'package:flutter/material.dart';
import 'package:get_it/get_it.dart';
import 'package:syncademic_app/repository/sync_profile_repository.dart';
import 'package:syncademic_app/widgets/sync_profiles_list.dart';

void main() {
  final getIt = GetIt.instance;

  // Register the SyncProfileRepository
  getIt.registerSingleton<SyncProfileRepository>(
      MockSyncProfileRepository()..createRandomData(10));

  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
        title: 'Syncademia',
        theme: ThemeData(
          colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
          useMaterial3: true,
        ),
        home: Scaffold(
          appBar: AppBar(
            title: const Text('Syncademia'),
          ),
          body: const SyncProfilesList(),
        ));
  }
}
