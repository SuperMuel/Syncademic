import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter/widgets.dart';
import 'package:get_time_ago/get_time_ago.dart';

class TimeAgoBuilder extends StatefulWidget {
  const TimeAgoBuilder(
      {super.key,
      required this.dt,
      this.builder,
      this.refreshRate = const Duration(seconds: 1)});

  final DateTime dt;
  final Duration refreshRate;

  /// A builder that is called with the current last sync time.
  final Function(BuildContext context, String timeAgo)? builder;

  @override
  State<TimeAgoBuilder> createState() => _TimeAgoBuilderState();
}

class _TimeAgoBuilderState extends State<TimeAgoBuilder> {
  late Timer _timer;

  @override
  void initState() {
    super.initState();
    _timer = Timer.periodic(widget.refreshRate, (timer) {
      setState(() => updateLastSync(widget.dt));
    });
  }

  updateLastSync(DateTime lastSync) {
    _lastSync = GetTimeAgo.parse(lastSync);
  }

  String _lastSync = 'unknown';

  @override
  void dispose() {
    _timer.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return widget.builder?.call(context, _lastSync) ?? Text(_lastSync);
  }
}
