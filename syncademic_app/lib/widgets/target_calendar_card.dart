import 'package:flutter/material.dart';

import '../models/target_calendar.dart';

class TargetCalendarCard extends StatelessWidget {
  final TargetCalendar targetCalendar;
  final VoidCallback onPressed;

  const TargetCalendarCard({
    super.key,
    required this.targetCalendar,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      child: InkWell(
        onTap: onPressed,
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Row(
            children: [
              //image icon
              Image.asset(
                "assets/icons/google_calendar_icon_1024x1024.png",
                width: 48,
                height: 48,
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Text(
                  targetCalendar.title,
                  style: Theme.of(context).textTheme.titleLarge,
                ),
              ),
              IconButton(
                icon: const Icon(Icons.edit),
                onPressed: onPressed,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
