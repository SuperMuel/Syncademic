import 'package:flutter/material.dart';
import 'package:syncademic_app/models/provider_account.dart';

class ProviderIcon extends StatelessWidget {
  final Provider provider;
  const ProviderIcon({super.key, required this.provider});

  @override
  Widget build(BuildContext context) {
    return switch (provider) {
      Provider.google => Image.asset(
          'assets/icons/google_icon_128.png',
          width: 32,
          height: 32,
        ),
    };
  }
}

class ProviderAccountCard extends StatelessWidget {
  const ProviderAccountCard({super.key, required this.providerAccount});

  final ProviderAccount providerAccount;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Row(
          children: [
            ProviderIcon(provider: providerAccount.provider),
            const SizedBox(width: 16),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  "${providerAccount.provider.name} Account",
                  style: Theme.of(context).textTheme.labelLarge,
                ),
                Text(providerAccount.providerAccountEmail),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
