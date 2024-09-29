import 'package:flutter/material.dart';
import 'package:sign_in_button/sign_in_button.dart';

import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_svg/svg.dart';
import 'package:get_it/get_it.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';

import '../authentication/cubit/auth_cubit.dart';

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
              body: Container(
                  height: double.infinity,
                  width: double.infinity,
                  decoration: const BoxDecoration(
                    gradient: LinearGradient(
                      colors: [Colors.blueAccent, Colors.purpleAccent],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                  ),
                  child: SingleChildScrollView(
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Center(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.center,
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            SvgPicture.asset(
                              'assets/icons/syncademic-icon.svg',
                              semanticsLabel: 'Syncademic logo',
                              colorFilter: const ColorFilter.mode(
                                Colors.white,
                                BlendMode.srcIn,
                              ),
                              height: MediaQuery.of(context).size.height * 0.5,
                            ),
                            const SizedBox(height: 30),

                            Text('Syncademic',
                                style: GoogleFonts.montserrat(
                                    fontSize:
                                        MediaQuery.of(context).size.width > 320
                                            ? 48.0
                                            : 36.0,
                                    fontWeight: FontWeight.bold,
                                    color: Colors.white)),
                            const SizedBox(height: 16),
                            Text(
                              'Synchronize your academic life with your digital world.',
                              style: GoogleFonts.montserrat(
                                  fontSize: 20.0, color: Colors.white70),
                              textAlign: TextAlign.center,
                            ),

                            const SizedBox(height: 32),

                            SignInButton(
                              Buttons.google,
                              onPressed: authBloc.signInWithGoogle,
                            ),
                            // Get Started button
                          ]
                              .animate(
                                interval: const Duration(milliseconds: 60),
                              )
                              .fadeIn()
                              .scale(
                                curve: Curves.easeInOutBack,
                                delay: const Duration(milliseconds: 200),
                              ),
                        ),
                      ),
                    ),
                  )));
        });
  }
}
