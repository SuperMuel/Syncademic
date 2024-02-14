import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:get_it/get_it.dart';
import 'package:go_router/go_router.dart';

import '../../authentication/cubit/auth_cubit.dart';

// TODO : add loading state

class GoogleSignInPage extends StatelessWidget {
  const GoogleSignInPage({super.key});

  @override
  Widget build(BuildContext context) {
    final bloc = GetIt.I<AuthCubit>();

    return BlocConsumer<AuthCubit, AuthState>(
      bloc: bloc,
      listener: (context, state) {
        state.maybeWhen(
            orElse: () {},
            authenticated: (_) {
              context.go('/');
            });
      },
      builder: (context, state) => Scaffold(
        appBar: AppBar(
          title: const Text('Sign in with Google'),
        ),
        body: Center(
          child: ElevatedButton(
            onPressed: bloc.signInWithGoogle,
            child: const Text('Sign in with Google'),
          ),
        ),
      ),
    );
  }
}
