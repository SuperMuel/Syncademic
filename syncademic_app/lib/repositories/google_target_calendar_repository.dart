import 'package:cloud_functions/cloud_functions.dart';
import 'package:get_it/get_it.dart';
import '../models/id.dart';
import '../models/provider_account.dart';
import '../models/target_calendar.dart';
import 'target_calendar_repository.dart';

class GoogleTargetCalendarRepository implements TargetCalendarRepository {
  GoogleTargetCalendarRepository({FirebaseFunctions? functions})
      : functions = functions ?? GetIt.I.get<FirebaseFunctions>();

  final FirebaseFunctions functions;

  @override
  Future<List<TargetCalendar>> getCalendars(
      ProviderAccount providerAccount) async {
    final result = await functions
        .httpsCallable('list_user_calendars')
        .call({'providerAccountId': providerAccount.providerAccountId});

    final calendars = result.data['calendars'] as List<dynamic>;

    return calendars
        .map((calendar) => TargetCalendar(
              id: ID.fromString(calendar['id']),
              title: calendar['summary'] ?? 'Unnamed calendar',
              description: calendar['description'],
              providerAccountId: providerAccount.providerAccountId,
              providerAccountEmail: providerAccount.providerAccountEmail,
            ))
        .toList();
  }
}
