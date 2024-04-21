import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter/widgets.dart';
import 'package:gap/gap.dart';

import '../models/target_calendar.dart';

class TargetCalendarCard extends StatelessWidget {
  final TargetCalendar targetCalendar;
  final VoidCallback? onPressed;

  final bool showEditIcon;
  const TargetCalendarCard({
    super.key,
    required this.targetCalendar,
    this.onPressed,
    this.showEditIcon = false,
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
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              //image icon
              Image.asset(
                "assets/icons/google_calendar_icon_1024x1024.png",
                width: 48,
                height: 48,
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      // TODO : stack the icon button instead of aligning it to the right to prevent UI jank
                      children: [
                        Flexible(
                          child: Text(
                            targetCalendar.title,
                            style: Theme.of(context).textTheme.titleLarge,
                          ),
                        ),
                        if (showEditIcon)
                          IconButton(
                            icon: const Icon(Icons.edit),
                            onPressed: onPressed,
                          ),
                      ],
                    ),
                    if (targetCalendar.description != null) ...[
                      Text(
                        targetCalendar.description!,
                        style: Theme.of(context).textTheme.bodySmall,
                      )
                    ]
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
