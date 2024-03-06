import 'package:flutter/material.dart';
import '../models/target_calendar.dart';

class TargetCalendarCard extends StatelessWidget {
  final TargetCalendar targetCalendar;
  const TargetCalendarCard({super.key, required this.targetCalendar});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        title: Text(targetCalendar.title),
      ),
    );
  }
}
