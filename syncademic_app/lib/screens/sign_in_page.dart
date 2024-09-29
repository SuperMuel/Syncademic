import 'package:flutter/material.dart';

import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_svg/svg.dart';
import 'package:get_it/get_it.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';

import '../authentication/cubit/auth_cubit.dart';

class GoogleSignInButton extends StatelessWidget {
  final VoidCallback onTap;

  const GoogleSignInButton({super.key, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return OutlinedButton(
      onPressed: onTap,
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 15),
        child: Center(
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Image.asset(
                'assets/icons/google_icon_128.png',
                height: 20,
                width: 20,
              ),
              const SizedBox(width: 10),
              Text(
                'Sign in with Google',
                style: GoogleFonts.roboto(
                  fontSize: 16,
                  fontWeight: FontWeight.w500,
                  color: Colors.black54,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class SignInPage extends StatelessWidget {
  const SignInPage({super.key});

  @override
  Widget build(BuildContext context) {
    final authBloc = GetIt.I<AuthCubit>();

    return BlocConsumer<AuthCubit, AuthState>(
      bloc: authBloc,
      listener: (context, state) {
        state.maybeMap(
          orElse: () {},
          authenticated: (state) {
            context.go('/');
          },
          unauthenticated: (state) {
            if (state.errorMessage != null) {
              ScaffoldMessenger.of(context)
                ..hideCurrentSnackBar()
                ..showSnackBar(
                  SnackBar(
                    content: Text(state.errorMessage!),
                  ),
                );
            }
          },
        );
      },
      builder: (context, state) {
        return Scaffold(
          appBar: AppBar(
            title: Row(
              children: [
                SvgPicture.asset(
                  'assets/icons/syncademic-icon.svg',
                  semanticsLabel: 'Syncademic logo',
                  colorFilter: const ColorFilter.mode(
                    Color(0xff16314d),
                    BlendMode.srcIn,
                  ),
                  height: 40,
                ),
                const SizedBox(width: 16),
                Text(
                  'Syncademic',
                  style: GoogleFonts.roboto(
                    fontSize: 24,
                    fontWeight: FontWeight.w400,
                    color: const Color(0xff16314d),
                  ),
                ),
              ],
            ),
          ),
          body: SafeArea(
            child: LayoutBuilder(
              builder: (context, constraints) {
                // Check if the width is greater than 600 (desktop)
                if (constraints.maxWidth > 600) {
                  return _buildDesktopLayout(context, authBloc);
                } else {
                  return _buildMobileLayout(context, authBloc);
                }
              },
            ),
          ),
        );
      },
    );
  }

  Widget _buildDesktopLayout(BuildContext context, AuthCubit authBloc) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32.0),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.center,
          mainAxisSize: MainAxisSize.min,
          children: [
            ClipRRect(
              borderRadius: BorderRadius.circular(16),
              child: Image.asset(
                'assets/illustrations/little_boy.jpeg',
                fit: BoxFit.cover,
                width: MediaQuery.of(context).size.width * 0.3,
              ),
            ),
            const SizedBox(width: 50),
            ConstrainedBox(
              constraints: BoxConstraints(
                maxHeight: MediaQuery.of(context).size.height * 0.7,
              ),
              child: _buildContentColumn(context, authBloc, isMobile: false),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMobileLayout(BuildContext context, AuthCubit authBloc) {
    return SingleChildScrollView(
      child: ConstrainedBox(
        constraints: BoxConstraints(
          minHeight: MediaQuery.of(context).size.height -
              MediaQuery.of(context).padding.top,
        ),
        child: IntrinsicHeight(
          child: Padding(
            padding: const EdgeInsets.all(32.0),
            child: _buildContentColumn(context, authBloc, isMobile: true),
          ),
        ),
      ),
    );
  }

  Widget _buildTextAndSubtext(
    BuildContext context,
    AuthCubit authBloc,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Welcome,',
            style: GoogleFonts.roboto(
                fontSize: 32,
                fontWeight: FontWeight.w600,
                color: const Color(0xff16314d))),
        Text('Sign in to continue',
            style: GoogleFonts.roboto(
                fontSize: 20, color: const Color(0xff16314d))),
      ],
    );
  }

  Widget _buildContentColumn(BuildContext context, AuthCubit authBloc,
      {required bool isMobile}) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.start,
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: [
        if (isMobile) ...[
          ClipRRect(
            borderRadius: BorderRadius.circular(16),
            child: Image.asset('assets/illustrations/little_boy.jpeg'),
          ),
          const SizedBox(height: 32),
        ],
        _buildTextAndSubtext(context, authBloc),
        const SizedBox(height: 32),
        !isMobile
            ? ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 300),
                child: GoogleSignInButton(
                  onTap: authBloc.signInWithGoogle,
                ),
              )
            : GoogleSignInButton(
                onTap: authBloc.signInWithGoogle,
              ),
      ],
    );
  }
}
