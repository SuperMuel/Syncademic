import 'package:flutter/material.dart';
import 'package:sign_in_button/sign_in_button.dart';

import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_svg/svg.dart';
import 'package:get_it/get_it.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';

import '../authentication/cubit/auth_cubit.dart';

class LogoAndSyncademic extends StatelessWidget {
  const LogoAndSyncademic({super.key});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16.0),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          SvgPicture.asset(
            'assets/icons/syncademic-icon.svg',
            semanticsLabel: 'Syncademic logo',
            colorFilter: const ColorFilter.mode(
              Color(0xff16314d),
              BlendMode.srcIn,
            ),
            height: 48,
          ),
          const SizedBox(width: 16),
          Text(
            'Login',
            style: GoogleFonts.roboto(
              fontSize: 32,
              fontWeight: FontWeight.w600,
              color: const Color(0xff16314d),
            ),
          ),
        ],
      ),
    );
  }
}

class GoogleSignInButton extends StatelessWidget {
  final VoidCallback onTap;

  const GoogleSignInButton({super.key, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: double
            .infinity, // This line ensures the button takes all available width
        decoration: BoxDecoration(
          border: Border.all(color: Colors.grey),
          borderRadius: BorderRadius.circular(32),
        ),
        padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 15),
        child: Row(
          mainAxisAlignment: MainAxisAlignment
              .center, // This line centers the content horizontally
          children: [
            Image.asset(
              'assets/icons/google_icon_128.png', // Your Google logo asset path
              height: 20, // Adjust height as needed
              width: 20, // Adjust width as needed
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
        // ... existing listener code ...
      },
      builder: (context, state) {
        return Scaffold(
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
    return Padding(
      padding: const EdgeInsets.all(32.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Expanded(
            flex: 1,
            child: ClipRRect(
              borderRadius: BorderRadius.circular(16),
              child: Image.asset(
                'assets/illustrations/little_boy.jpeg',
                fit: BoxFit.cover,
                height: double.infinity,
              ),
            ),
          ),
          const SizedBox(width: 32),
          Expanded(
            flex: 1,
            child: _buildContentColumn(context, authBloc, false),
          ),
        ],
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
            child: _buildContentColumn(context, authBloc, true),
          ),
        ),
      ),
    );
  }

  Widget _buildContentColumn(
      BuildContext context, AuthCubit authBloc, bool isMobile) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.max,
      children: [
        if (isMobile)
          ClipRRect(
            borderRadius: BorderRadius.circular(16),
            child: Image.asset('assets/illustrations/little_boy.jpeg'),
          ),
        if (isMobile) const SizedBox(height: 32),
        Text(
          'Welcome,',
          style: GoogleFonts.roboto(
            fontSize: 32,
            fontWeight: FontWeight.w600,
            color: const Color(0xff16314d),
          ),
        ),
        const SizedBox(height: 8),
        Text(
          'Sign in to continue',
          style: GoogleFonts.roboto(
            fontSize: 20,
            color: const Color(0xff16314d),
          ),
        ),
        if (isMobile) const Spacer() else const SizedBox(height: 32),
        Center(
          child: GoogleSignInButton(
            onTap: authBloc.signInWithGoogle,
          ),
        ),
      ],
    );
  }
}
