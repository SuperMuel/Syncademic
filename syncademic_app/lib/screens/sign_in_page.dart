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
            'Syncademic',
            style: GoogleFonts.inter(
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
                child: Column(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                ClipRRect(
                  borderRadius: BorderRadius.circular(16),
                  child: Image.asset('assets/illustrations/little_boy.jpeg'),
                ),
                const SizedBox(height: 32),
                const LogoAndSyncademic(),
                const SizedBox(height: 32),
                SignInButton(
                  Buttons.google,
                  onPressed: authBloc.signInWithGoogle,
                ),
              ],
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
