import 'package:flutter/material.dart';
import '../models/provider_account.dart';

import '../models/id.dart';
import '../models/target_calendar.dart';

enum GoogleCalendarColor {
  brown('1', Color(0xFFAC725E)),
  red('2', Color(0xFFD06B64)),
  brightRed('3', Color(0xFFF83A22)),
  orange('4', Color(0xFFFA573C)),
  brightOrange('5', Color(0xFFFF7537)),
  yellow('6', Color(0xFFFFAD46)),
  green('7', Color(0xFF42D692)),
  darkGreen('8', Color(0xFF16A765)),
  lightGreen('9', Color(0xFF7BD148)),
  paleGreen('10', Color(0xFFB3DC6C)),
  paleYellow('11', Color(0xFFFBE983)),
  lightYellow('12', Color(0xFFFAD165)),
  turquoise('13', Color(0xFF92E1C0)),
  lightTurquoise('14', Color(0xFF9FE1E7)),
  lightBlue('15', Color(0xFF9FC6E7)),
  blue('16', Color(0xFF4986E7)),
  lavender('17', Color(0xFF9A9CFF)),
  purple('18', Color(0xFFB99AFF)),
  gray('19', Color(0xFFC2C2C2)),
  slateGray('20', Color(0xFFCABDBF)),
  pink('21', Color(0xFFCCA6AC)),
  lightPink('22', Color(0xFFF691B2)),
  magenta('23', Color(0xFFCD74E6)),
  plum('24', Color(0xFFA47AE2));

  final String id;

  final Color color;

  const GoogleCalendarColor(this.id, this.color);

  static GoogleCalendarColor fromId(String id) {
    return GoogleCalendarColor.values.firstWhere(
      (e) => e.id == id,
      orElse: () => throw ArgumentError('Invalid color ID: $id'),
    );
  }

  static GoogleCalendarColor fromColor(Color color) {
    return GoogleCalendarColor.values.firstWhere(
      (e) => e.color == color,
      orElse: () => throw ArgumentError('Invalid color: $color'),
    );
  }
}

abstract class TargetCalendarRepository {
  Future<List<TargetCalendar>> getCalendars(ProviderAccount providerAccount);
}

class MockTargetCalendarRepository implements TargetCalendarRepository {
  final List<TargetCalendar> _calendars = List.generate(
    10,
    (index) => TargetCalendar(
      id: ID.fromString('target-google-calendar-$index'),
      title: 'Calendar $index',
      description: 'Description of calendar $index',
      providerAccountId: 'providerAccountId',
      providerAccountEmail: 'providerAccountEmail',
    ),
  );

  @override
  Future<List<TargetCalendar>> getCalendars(
          ProviderAccount providerAccount) async =>
      _calendars;
}
