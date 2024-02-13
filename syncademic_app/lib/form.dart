import 'package:flutter/material.dart';
import 'package:gap/gap.dart';

class NewSyncConfigForm extends StatelessWidget {
  const NewSyncConfigForm({super.key});

  @override
  Widget build(BuildContext context) {
    // A form with an "ICS url" text field
    // and a "Sync" button
    return Scaffold(
      appBar: AppBar(
        title: const Text('New synchronization configuration'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: <Widget>[
            TextFormField(
              decoration: const InputDecoration(
                  labelText: 'ICS url', border: OutlineInputBorder()),
            ),
            const Gap(16),
            const ElevatedButton(
              onPressed: null,
              child: Text('Synchronize'),
            ),
          ],
        ),
      ),
    );
  }
}
