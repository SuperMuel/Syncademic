import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:get_it/get_it.dart';
import 'package:go_router/go_router.dart';

import '../../authentication/cubit/auth_cubit.dart';

// TODO: Add remove account button

class AccountPage extends StatelessWidget {
  const AccountPage({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<AuthCubit, AuthState>(
      bloc: GetIt.I<AuthCubit>(),
      builder: (context, state) {
        return Scaffold(
          appBar: AppBar(
            title: const Text('Account'),
            actions: [
              IconButton(
                icon: const Icon(Icons.logout),
                onPressed: () => GetIt.I<AuthCubit>()
                    .signOut()
                    .then((value) => context.go('/')),
                tooltip: "Sign out",
              ),
            ],
          ),
          body: state.maybeMap(
            orElse: () => const Center(child: CircularProgressIndicator()),
            authenticated: (user) => Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text('Id : ${user.user.id}'),
                  Text('Email : ${user.user.email}'),
                  //TODO : add created on
                ],
              ),
            ),
          ),
        );
      },
    );
  }
}
