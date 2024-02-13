import 'package:flutter/material.dart';
import 'package:syncademic_app/form.dart';
import 'package:syncademic_app/widgets/sync_profiles_list.dart';

void main() {
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
          body: const SyncProfilesList(
            profiles: [],
          ),
        ));
  }
}
