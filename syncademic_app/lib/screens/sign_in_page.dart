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
          state.maybeWhen(
              orElse: () {},
              authenticated: (_) {
                context.go('/');
              });
        },
        builder: (context, state) {
          return Scaffold(
            body: SafeArea(
                child: LayoutBuilder(
              builder: (context, contraints) => SingleChildScrollView(
                child: ConstrainedBox(
                  constraints: BoxConstraints(
                    minHeight: contraints.maxHeight,
                  ),
                  child: IntrinsicHeight(
                    child: Padding(
                      padding: const EdgeInsets.all(32.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        mainAxisSize: MainAxisSize.max,
                        children: [
                          ClipRRect(
                            borderRadius: BorderRadius.circular(16),
                            child: Image.asset(
                                'assets/illustrations/little_boy.jpeg'),
                          ),
                          const SizedBox(height: 32),
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
                          Spacer(),
                          Center(
                            child: GoogleSignInButton(
                              onTap: authBloc.signInWithGoogle,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
            )),
          );

          // return Scaffold(
          //     body: SingleChildScrollView(
          //   child: Padding(
          //     padding: const EdgeInsets.all(32.0),
          //     child: Row(
          //       mainAxisAlignment: MainAxisAlignment.center,
          //       children: [
          //         Flexible(
          //           child: Image.asset(
          //             'assets/illustrations/apple_devices_mockup_transparent_1600.png',
          //             fit: BoxFit.cover,
          //             width: MediaQuery.of(context).size.width > 600
          //                 ? 400
          //                 : MediaQuery.of(context).size.width,
          //           ),
          //         ),
          //         const SizedBox(width: 32),
          //         Flexible(
          //           flex: 2,
          //           child: Column(
          //             crossAxisAlignment: CrossAxisAlignment.start,
          //             mainAxisSize: MainAxisSize.min,
          //             children: [
          //               SvgPicture.asset(
          //                 'assets/icons/syncademic-icon.svg',
          //                 semanticsLabel: 'Syncademic logo',
          //                 colorFilter: const ColorFilter.mode(
          //                   //16314d
          //                   Color(0xff16314d),
          //                   BlendMode.srcIn,
          //                 ),
          //                 height: 64,
          //               ),
          //               const SizedBox(height: 16),
          //               Text(
          //                 "Welcome,",
          //                 style: GoogleFonts.montserrat(
          //                   fontSize: 32,
          //                   fontWeight: FontWeight.bold,
          //                   color: Colors.black,
          //                 ),
          //               ),
          //               Text(
          //                 "Sign in to continue",
          //                 style: GoogleFonts.montserrat(
          //                   fontSize: 20,
          //                   color: Colors.black,
          //                 ),
          //               ),
          //               const SizedBox(height: 32),

          //               SignInButton(
          //                 Buttons.google,
          //                 onPressed: authBloc.signInWithGoogle,
          //               ),
          //               // Get Started button
          //             ]
          //                 .animate(
          //                   interval: const Duration(milliseconds: 60),
          //                 )
          //                 .fadeIn()
          //                 .scale(
          //                   curve: Curves.easeInOutBack,
          //                   delay: const Duration(milliseconds: 200),
          //                 ),
          //           ),
          //         ),
          //       ],
          //     ),
          //   ),
          // ));
        });
  }
}
