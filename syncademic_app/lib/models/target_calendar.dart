import 'package:freezed_annotation/freezed_annotation.dart';

import 'id.dart';

part 'target_calendar.freezed.dart';

@freezed
class TargetCalendar with _$TargetCalendar {
  const factory TargetCalendar({
    /// The unique identifier for the calendar.
    ///
    /// For Google Calendar, this is the ID of the calendar provided by Google.
    required ID id,

    /// The title of the calendar, as provided by the calendar service.
    required String title,

    /// The description of the calendar, as provided by the calendar service.
    String? description,

    /// The unique identifier for the user account that owns the calendar.
    ///
    /// This identifier represents the specific user account associated with the calendar,
    /// and it varies depending on the calendar service being used.
    ///
    /// For Google Calendar:
    /// - The `providerAccountId` is the ID of the Google Account that owns the calendar.
    ///
    /// For Microsoft Outlook:
    /// - The `providerAccountId` is the ID of the Microsoft Outlook account that owns the calendar.
    ///
    /// Note: The `providerAccountId` is different from the `id` property, which represents the unique identifier
    /// of the calendar itself. It is also different from the user ID that is logged in to the Syncademic app,
    /// as a user can have multiple accounts on multiple calendar services.
    required String providerAccountId,
    required String providerAccountEmail,
    bool? createdBySyncademic,
  }) = _TargetCalendar;
}
