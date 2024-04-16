import 'package:flutter/material.dart';
import '../models/target_calendar.dart';

class TargetCalendarCard extends StatelessWidget {
  final TargetCalendar targetCalendar;
  final VoidCallback onPressed;

  const TargetCalendarCard({
    Key? key,
    required this.targetCalendar,
    required this.onPressed,
  }) : super(key: key);

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
              const Icon(
                Icons.calendar_today,
                size: 40,
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
