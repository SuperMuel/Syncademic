import 'package:flutter/material.dart';

import '../models/schedule_source.dart';

//TODO : add copy to clipboard button

class ScheduleSourceCard extends StatefulWidget {
  const ScheduleSourceCard({super.key, required this.scheduleSource});
  final ScheduleSource scheduleSource;

  @override
  State<ScheduleSourceCard> createState() => _ScheduleSourceCardState();
}

class _ScheduleSourceCardState extends State<ScheduleSourceCard> {
  bool expanded = false;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        isThreeLine: true,
        title: const Text("Url", style: TextStyle(fontWeight: FontWeight.bold)),
        leading: const Icon(Icons.link),
        subtitle: SelectableText(
          widget.scheduleSource.url,
          minLines: 1,
          maxLines: expanded ? 10 : 1,
          style: const TextStyle(
            fontSize: 16,
            overflow: TextOverflow.ellipsis,
          ),
        ),
        trailing: IconButton(
          icon: Icon(expanded ? Icons.expand_less : Icons.expand_more),
          onPressed: toggleExpanded,
        ),
        onTap: toggleExpanded,
      ),
    );
  }

  void toggleExpanded() => setState(() {
        expanded = !expanded;
      });
}
