import 'package:flutter/material.dart';

import '../models/target_calendar.dart';

class TargetCalendarCard extends StatelessWidget {
  final TargetCalendar targetCalendar;
  final VoidCallback? onPressed;
  final double maxWidth;

  final bool showEditIcon;
  const TargetCalendarCard({
    super.key,
    required this.targetCalendar,
    this.onPressed,
    this.showEditIcon = false,
    this.maxWidth = 500,
  });

  @override
  Widget build(BuildContext context) {
    return ConstrainedBox(
      constraints: BoxConstraints(maxWidth: maxWidth),
      child: Stack(
        children: [
          Card(
            elevation: 2,
            child: InkWell(
              onTap: onPressed,
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    //image icon
                    Image.asset(
                      "assets/icons/google_calendar_icon_1024x1024.png",
                      width: 48,
                      height: 48,
                    ),
                    const SizedBox(width: 16),
                    Flexible(
                      fit: FlexFit.loose,
                      child: Column(
                        children: [
                          Text(
                            targetCalendar.title,
                            style: Theme.of(context).textTheme.titleLarge,
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
          ),
          if (showEditIcon)
            Positioned(
              top: 0,
              right: 0,
              child: IconButton(
                icon: const Icon(Icons.edit),
                onPressed: onPressed,
              ),
            ),
        ],
      ),
    );
  }
}
