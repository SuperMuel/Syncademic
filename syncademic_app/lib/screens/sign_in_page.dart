import 'package:flutter/material.dart';

import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_svg/svg.dart';
import 'package:get_it/get_it.dart';
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
          children: [
            Expanded(
              flex: 1,
              child: ClipRRect(
                borderRadius: BorderRadius.circular(16),
                child: Image.asset(
                  'assets/illustrations/little_boy.jpeg',
                  fit: BoxFit.cover,
                ),
              ),
            ),
            const SizedBox(width: 32),
            Expanded(
              flex: 1,
              child: ConstrainedBox(
                constraints: BoxConstraints(
                  maxHeight: MediaQuery.of(context).size.height * 0.7,
                ),
                child: _buildContentColumn(context, authBloc, isMobile: false),
              ),
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
