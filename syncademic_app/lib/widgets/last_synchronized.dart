import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter/widgets.dart';
import 'package:get_time_ago/get_time_ago.dart';

class LastSynchronized extends StatefulWidget {
  const LastSynchronized(
      {super.key,
      required this.lastSync,
      this.builder,
      this.refreshRate = const Duration(seconds: 1)});

  final DateTime? lastSync;
  final Duration refreshRate;

  /// A builder that is called with the current last sync time.
  final Function(BuildContext context, String? lastSync)? builder;

  @override
  State<LastSynchronized> createState() => _LastSynchronizedState();
}

class _LastSynchronizedState extends State<LastSynchronized> {
  late Timer _timer;

  @override
  void initState() {
    super.initState();
    _timer = Timer.periodic(widget.refreshRate, (timer) {
      setState(() => updateLastSync(widget.lastSync));
    });
  }

  updateLastSync(DateTime? lastSync) {
    if (lastSync == null) {
      return _lastSync = 'unknown';
    }
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
